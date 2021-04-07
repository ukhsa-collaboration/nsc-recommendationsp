#
# Build the front end static files
#
FROM node:12.14.1 as FRONT_END_BUILD

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

FROM python:3.6

ENV SRC_ROOT=/opt/app-root/src/

# create a non root user to run as
ENV RUN_USER=django
RUN groupadd -r $RUN_USER && useradd --no-log-init -r -g $RUN_USER $RUN_USER

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
COPY --chown=${RUN_USER}:${RUN_USER} . ${SRC_ROOT}

USER $RUN_USER
RUN DJANGO_CONFIGURATION=Build python manage.py collectstatic --noinput; chown -R ${RUN_USER}:${RUN_USER} ${SRC_ROOT}../public

ENTRYPOINT ["./deploy/entrypoint.sh"]
CMD ["gunicorn", "-c", "gunicorn.conf.py", "nsc.wsgi"]
