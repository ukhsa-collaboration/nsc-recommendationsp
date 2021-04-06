#
# Build the front end static files
#
FROM node:12.14.1 as FRONT_END_BUILD

# get the pinned version of yarn
RUN npm install -g yarn@1.21.1 --force


WORKDIR /opt/apt-root/src/

# install yarn requirements
COPY package.json /opt/apt-root/src/
COPY yarn.lock /opt/apt-root/src/
RUN yarn install --pure-lockfile

# build the output
COPY frontend /opt/apt-root/src/frontend
COPY webpack.config.js /opt/apt-root/src/
RUN yarn build

#
# Build the backend image (incorporating the output from FRONT_END_BUILD)
#

FROM python:3.6

ENV SRC_ROOT=/opt/apt-root/src/
ENV RUN_USER=1001

RUN mkdir $SRC_ROOT -p; chown -R $RUN_USER:$RUN_USER $SRC_ROOT..
WORKDIR $SRC_ROOT

# Build process dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# copy the output from the frontend build
COPY --from=FRONT_END_BUILD --chown=1001:1001 ${SRC_ROOT}frontend/dist ${SRC_ROOT}frontend/dist

# install python dependencies
COPY requirements.txt ${SRC_ROOT}requirements.txt
RUN pip install -r ${SRC_ROOT}requirements.txt

# copy the source to the container
COPY --chown=1001:1001 . ${SRC_ROOT}

USER 1001

RUN DJANGO_CONFIGURATION=Build python manage.py collectstatic --noinput

CMD ["./deploy/entrypoint.sh"]
