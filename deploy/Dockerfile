#
# Build the front end static files
#
FROM image-registry.openshift-image-registry.svc:5000/openshift/node:12.14.1 as FRONT_END_BUILD

ENV SRC_ROOT=/opt/app-root/src/

# get the pinned version of yarn
RUN npm install -g yarn@1.21.1 --force

WORKDIR $SRC_ROOT

# install yarn requirements
COPY package.json ${SRC_ROOT}
COPY yarn.lock ${SRC_ROOT}
RUN yarn install --pure-lockfile

# build the output
COPY frontend ${SRC_ROOT}frontend
COPY webpack.config.js ${SRC_ROOT}
RUN yarn build

#
# Build the backend image (incorporating the output from FRONT_END_BUILD)
#

FROM image-registry.openshift-image-registry.svc:5000/openshift/python:3.6

ENV SHELL=/bin/bash
ENV SRC_ROOT=/opt/app-root/src/

RUN mkdir $SRC_ROOT -p
WORKDIR $SRC_ROOT

# Build process dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# copy the output from the frontend build
COPY --from=FRONT_END_BUILD ${SRC_ROOT}frontend/dist ${SRC_ROOT}frontend/dist

# install python dependencies
COPY requirements.txt ${SRC_ROOT}requirements.txt
RUN pip install -r ${SRC_ROOT}requirements.txt

# copy the source to the container
COPY . ${SRC_ROOT}

RUN DJANGO_CONFIGURATION=Build python manage.py collectstatic --noinput

ENTRYPOINT ["./deploy/entrypoint.sh"]
CMD ["gunicorn", "-c", "gunicorn.conf.py", "nsc.wsgi"]

# setup the container user so that is can be ran by an arbitrary user
# https://docs.openshift.com/container-platform/3.3/creating_images/guidelines.html#openshift-container-platform-specific-guidelines
RUN chgrp -R 0 ${SRC_ROOT}.. && \
    chmod -R g=u ${SRC_ROOT}..

USER 1001