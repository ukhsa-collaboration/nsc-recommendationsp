#!/bin/bash

export BUCKET_NAME=`cat /var/secrets/s3/bucket-name`
export BUCKET_ENDPOINT=`cat /var/secrets/s3/endpoint`
export BUCKET_HOST="${BUCKET_NAME}.${BUCKET_ENDPOINT}"

echo "Proxying: ${BUCKET_HOST}"
envsubst '$BUCKET_HOST' < ./nginx-cfg/bucket-proxy.nginx.config > $NGINX_CONF_TARGET

nginx -g 'daemon off;'
