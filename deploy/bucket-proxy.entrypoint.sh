#!/bin/bash

envsubst '$BUCKET_HOST' < ./nginx-cfg/bucket-proxy.nginx.config > $NGINX_CONF_TARGET

nginx -g 'daemon off;'
