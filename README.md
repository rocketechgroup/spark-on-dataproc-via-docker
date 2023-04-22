# Run serverless spark on Dataproc

## Generate random file
```
gshuf -n 50000 /usr/share/dict/words | tr '\n' ' ' > random_words.txt
```

## Build the spark custom docker image
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
Set image version
> This is available after pushing to Artifact Registry
```
export IMAGE_VERSION=[IMAGE_VERSION]
```

Set bucket name for processing
```
export PROCESS_BUCKET=[PROCESS_BUCKET]
```

Set Service account to use for the customer
> please note SA must have at least the following permissions `Artifact Registry Reader,Dataproc WorkerStorage Object Admin`
```
export SPARK_SA=[SPARK_SA]
```

Set network (when not using default network)
```
export SUBNET=[SUBNET]
```

Open network firewall rules so workers can talk to each other & master node, `or it won't work`
```
gcloud compute firewall-rules create allow-internal-ingress \
--network="[network-name]" \
--source-ranges="[subnetwork internal-IP ranges]" \
--direction="ingress" \
--action="allow" \
--rules="all"
```

Submit the job
```
gcloud dataproc batches submit pyspark wordcount.py \
--batch wordcount-$(date +"%Y%m%d-%H%M%S") \
--project ${PROJECT_ID} \
--region ${REGION} \
--container-image "europe-west2-docker.pkg.dev/${PROJECT_ID}/${AF_REPO_NAME}/${IMAGE_NAME}:${IMAGE_VERSION}" \
--deps-bucket ${PROCESS_BUCKET} \
--service-account ${SPARK_SA} \
--subnet ${SUBNET} \
-- gs://[input bucket]/random_words.txt gs://[output bucket]
```

## Run locally
```
spark-submit wordcount.py ./example//random_words.txt /tmp
```