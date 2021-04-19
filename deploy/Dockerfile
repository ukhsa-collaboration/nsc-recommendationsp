#
# Build the backend image (incorporating the output from FRONT_END_BUILD)
#

#
# NOTE: Requires the compiled static from the frontend to be built
#       This is handled in openshift
#

FROM centos/python-36-centos7

USER root

ENV SHELL=/bin/bash
ENV SRC_ROOT=/opt/app-root/src/

RUN mkdir $SRC_ROOT -p
WORKDIR $SRC_ROOT

# install python dependencies
RUN pip install -U pip
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