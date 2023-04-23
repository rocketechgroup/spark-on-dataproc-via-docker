import json
import os

import requests

from datetime import datetime
from google.auth import default
from google.auth.transport.requests import Request
from flask import Flask, render_template

PROJECT_ID = os.environ.get('PROJECT_ID')
REGION = os.environ.get('REGION')

METADATA_URL = 'http://metadata.google.internal/computeMetadata/v1/'
METADATA_HEADERS = {'Metadata-Flavor': 'Google'}
SERVICE_ACCOUNT = 'default'

AF_REPO_NAME = os.environ.get('AF_REPO_NAME')
IMAGE_NAME = os.environ.get('IMAGE_NAME')
IMAGE_VERSION = os.environ.get('IMAGE_VERSION')
PROCESS_BUCKET = os.environ.get('PROCESS_BUCKET')
SPARK_SA = os.environ.get('SPARK_SA')
SUBNET = os.environ.get('SUBNET')

PYTHON_FILE_URL = os.environ.get('PYTHON_FILE_URL')
SOURCE_INPUT_LOCATION = os.environ.get('SOURCE_INPUT_LOCATION')
TARGET_OUTPUT_LOCATION = os.environ.get('TARGET_OUTPUT_LOCATION')


def get_access_token():
    """
    This works on any GCP service, i.e. cloud run
    :return: access_token
    """
    try:
        url = '{}instance/service-accounts/{}/token'.format(
            METADATA_URL, SERVICE_ACCOUNT)

        # Request an access token from the metadata server.
        r = requests.get(url, headers=METADATA_HEADERS)
        r.raise_for_status()

        # Extract the access token from the response.
        access_token = r.json()['access_token']
    except requests.exceptions.ConnectionError:
        return None

    return access_token


def get_default_access_token():
    """
    This works only locally for development
    :return: access_token
    """
    # Obtain the default credentials
    credentials, project_id = default()

    # Refresh the credentials if necessary
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

    # Obtain the access token from the credentials
    return credentials.token


def spark_submit(python_file_url, source_input, target_output):
    timestamp = datetime.now()
    formatted_timestamp = timestamp.strftime("%Y%m%d-%H%M%S")
    dataproc_batch_url = f"https://dataproc.googleapis.com/v1/projects/{PROJECT_ID}/locations/{REGION}/batches?batch_id={IMAGE_NAME}-{formatted_timestamp}"

    payload = {
        "runtimeConfig": {
            "version": "2.0",
            "containerImage": f"europe-west2-docker.pkg.dev/{PROJECT_ID}/{AF_REPO_NAME}/{IMAGE_NAME}:{IMAGE_VERSION}",
            "properties": {
                "spark.dynamicAllocation.executorAllocationRatio": "1.0",
                "spark.dynamicAllocation.initialExecutors": "2",
                "spark.dynamicAllocation.minExecutors": "2",
                "spark.dynamicAllocation.maxExecutors": "50"
            }
        },
        "environmentConfig": {
            "executionConfig": {
                "serviceAccount": SPARK_SA,
                "subnetworkUri": SUBNET,
                "stagingBucket": PROCESS_BUCKET

            }
        },

        "pysparkBatch": {
            "mainPythonFileUri": python_file_url,
            "args": [source_input, target_output]
        }
    }

    if get_access_token():
        bearer_token = get_access_token()
    else:
        bearer_token = get_default_access_token()

    headers = {'Authorization': f'Bearer {bearer_token}', 'Content-Type': 'application/json'}
    response = requests.post(url=dataproc_batch_url, headers=headers, json=payload)
    response_content = json.loads(response.content)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        return response_content['error']['message']

    return response_content


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    response = spark_submit(
        python_file_url=PYTHON_FILE_URL,
        source_input=SOURCE_INPUT_LOCATION,
        target_output=TARGET_OUTPUT_LOCATION
    )
    return response


if __name__ == '__main__':
    app.run(debug=True)
