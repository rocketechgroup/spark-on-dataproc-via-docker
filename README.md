# Run serverless spark on Dataproc

## Generate random file

This command will generate a 260MB file with random words, you can upload it to GCS to test Dataproc

```
openssl rand -out example/sample_1.txt -base64 $(( 2**28 * 3/4 ))
```

## Run spark on serverless dataproc

### Env vars

```
export PROJECT_ID=[PROJECT_ID]
export REGION=[REGION]
export AF_REPO_NAME=[AF_REPO_NAME]
export IMAGE_NAME=[IMAGE_NAME]
export COMMIT_SHA=$(git rev-parse --short=8 HEAD)
```

### Create Artifact Registry repo

```
gcloud artifacts repositories create ${AF_REPO_NAME} --repository-format=docker --location=${REGION}
```

### Build Image

```
gcloud builds submit --config cloudbuild.yaml --substitutions _PROJECT_ID=${PROJECT_ID},_REPO_NAME=${AF_REPO_NAME},_IMAGE_NAME=${IMAGE_NAME},_COMMIT_SHA=${COMMIT_SHA}
```

## Submit serverless spark

### Set image version

> This is available after pushing to Artifact Registry

```
export IMAGE_VERSION=[IMAGE_VERSION]
```

### Set bucket name for processing

```
export PROCESS_BUCKET=[PROCESS_BUCKET]
```

### Set Service account to use for Dataproc

> Please note SA must have at least the following roles: `Artifact Registry Reader,Dataproc Worker, Storage Object Admin`

```
export SPARK_SA=[SPARK_SA]
```

### Set network (when not using default network)

```
export SUBNET=[SUBNET]
```

### Open network firewall rules so workers can talk to each other & master node, `or it won't work`

```
gcloud compute firewall-rules create allow-internal-ingress \
--network="[network-name]" \
--source-ranges="[subnetwork internal-IP ranges]" \
--direction="ingress" \
--action="allow" \
--rules="all"
```

### Submit the job via gcloud

```
gcloud dataproc batches submit pyspark gs://[workcound code bucket]/wordcount.py \
--batch wordcount-$(date +"%Y%m%d-%H%M%S") \
--project ${PROJECT_ID} \
--region ${REGION} \
--container-image "europe-west2-docker.pkg.dev/${PROJECT_ID}/${AF_REPO_NAME}/${IMAGE_NAME}:${IMAGE_VERSION}" \
--deps-bucket ${PROCESS_BUCKET} \
--service-account ${SPARK_SA} \
--subnet ${SUBNET} \
--version 2.0 \
--properties spark.dynamicAllocation.executorAllocationRatio=1.0,spark.dynamicAllocation.initialExecutors=3,spark.dynamicAllocation.minExecutors=3,spark.dynamicAllocation.maxExecutors=50 \
-- gs://[input bucket]/ gs://[output bucket]
```

### Submit the job via python

Why does this matter? Assume you have to execute the job from cloud composer or cloud run. This can become handy

```
python dataproc_submit.py "gs://[code bucket]/wordcount.py" \
    "gs://[input bucket]/" \
    "gs://[output bucket]"
```

### Run locally

```
spark-submit wordcount.py "./example/*.txt" /tmp
```

## Deploy the dataproc-trigger-app to trigger dataproc job
> Move working directory to `dataproc-trigger-app` before running the commands below

Additional App env var requires
```
export APP_SA=[APP_SA]
export APP_IMAGE_NAME=[APP_IMAGE_NAME]
export PYTHON_FILE_URL=[PYTHON_FILE_URL]
export SOURCE_INPUT_LOCATION=[SOURCE_INPUT_LOCATION]
export TARGET_OUTPUT_LOCATION=[SOURCE_INPUT_LOCATION]
```

> The service account here will require the following roles: `Dataproc Administrator`, `Service Account Token Creator` and `Service Account User`

Build & Deploy
```
gcloud builds submit --config cloudbuild.yaml --substitutions _PROJECT_ID=${PROJECT_ID},_REGION=${REGION},_SA=${APP_SA},_AF_REPO_NAME=${AF_REPO_NAME},_IMAGE_NAME=${IMAGE_NAME},_APP_IMAGE_NAME=${APP_IMAGE_NAME},_COMMIT_SHA=${COMMIT_SHA},_IMAGE_VERSION=${IMAGE_VERSION},_PROCESS_BUCKET=${PROCESS_BUCKET},_SPARK_SA=${SPARK_SA},_SUBNET=${SUBNET},_PYTHON_FILE_URL=${PYTHON_FILE_URL},_SOURCE_INPUT_LOCATION=${SOURCE_INPUT_LOCATION},_TARGET_OUTPUT_LOCATION=${TARGET_OUTPUT_LOCATION}
```