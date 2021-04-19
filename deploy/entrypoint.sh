#!/bin/bash

python manage.py migrate

echo "Running: $@"
eval "$@"
