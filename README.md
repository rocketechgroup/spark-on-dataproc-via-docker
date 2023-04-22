# Run serverless spark on Dataprod

## Generate random file
```
gshuf -n 50000 /usr/share/dict/words | tr '\n' ' ' > random_words.txt
```

## Build the spark custom docker image
```
export PROJECT_ID=[PROJECT_ID]
export AF_REPO_NAME=[AF_REPO_NAME]
export IMAGE_NAME=[IMAGE_NAME]
export COMMIT_SHA=$(git rev-parse --short=8 HEAD)
```

## Run locally
```
spark-submit wordcount.py gs://rocketech-de-pgcp-sandbox-serverless-spark-input/random_words.txt
```