FROM centos/nginx-116-centos7

USER root

RUN echo "" > /opt/app-root/src/not-found.html

COPY deploy/bucket-proxy.nginx.config ./nginx-cfg/
COPY deploy/bucket-proxy.entrypoint.sh ./entrypoint.sh
RUN chmod +x entrypoint.sh
# setup the container user so that is can be ran by an arbitrary user
# https://docs.openshift.com/container-platform/3.3/creating_images/guidelines.html#openshift-container-platform-specific-guidelines
RUN chgrp -R 0 /etc/nginx
RUN chgrp -R 0 . && chmod -R g=u .

USER 1001

ENTRYPOINT [ "./entrypoint.sh" ]