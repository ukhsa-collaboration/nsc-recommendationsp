FROM centos/nginx-116-centos7

ENV NGINX_ETC_ROOT=/etc/opt/rh/rh-nginx*
ENV NGINX_VAR_ROOT=/var/opt/rh/rh-nginx*
ENV NGINX_CONF_TARGET=${NGINX_ETC_ROOT}/nginx/nginx.conf

USER root

COPY deploy/bucket-proxy.nginx.config ./nginx-cfg/
COPY deploy/bucket-proxy.entrypoint.sh ./entrypoint.sh
RUN chmod +x entrypoint.sh
# setup the container user so that is can be ran by an arbitrary user
# https://docs.openshift.com/container-platform/3.3/creating_images/guidelines.html#openshift-container-platform-specific-guidelines
RUN chgrp -R 0 ${NGINX_CONF_TARGET} && chmod -R g=u ${NGINX_CONF_TARGET}
RUN chgrp -R 0 . && chmod -R g=u .

USER 1001

ENTRYPOINT [ "./entrypoint.sh" ]