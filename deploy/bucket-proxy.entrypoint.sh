#!/bin/bash

set -e

if [[ -z ${BUCKET_NAME+x} ]]; then
  echo "Loading BUCKET_NAME from secret"

  export BUCKET_NAME_SECRET_PATH=/run/secrets/s3/bucket-name
  if [ ! -f ${BUCKET_NAME_SECRET_PATH} ]; then
    echo "${BUCKET_NAME_SECRET_PATH} does not exist"
    exit
  fi

  export BUCKET_NAME=`cat ${BUCKET_NAME_SECRET_PATH}`
fi

if [[ -z ${BUCKET_ENDPOINT+x} ]]; then
  echo "Loading BUCKET_ENDPOINT from secret"

  export ENDPOINT_SECRET_PATH=/run/secrets/s3/endpoint
  if [ ! -f ${ENDPOINT_SECRET_PATH} ]; then
    echo "${ENDPOINT_SECRET_PATH} does not exist"
    exit
  fi

  export BUCKET_ENDPOINT=`cat ${ENDPOINT_SECRET_PATH}`
fi

export BUCKET_HOST="${BUCKET_NAME}.${BUCKET_ENDPOINT}"

echo "Proxying: ${BUCKET_HOST}"
envsubst '$BUCKET_HOST' < ./nginx-cfg/bucket-proxy.nginx.config > /etc/nginx/nginx.conf

nginx -g 'daemon off;'
