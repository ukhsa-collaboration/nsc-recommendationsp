FROM registry.access.redhat.com/ubi8/ubi

RUN dnf install -y epel-release && \
    dnf install -y clamav clamav-update && \
    dnf clean all && \
    freshclam

CMD ["clamd", "-F"]
