FROM python:3.12-slim

RUN mkdir /build
WORKDIR /build

# Build process dependencies
RUN find /etc/apt/ -name '*.list' -exec sed -i -e 's|http://deb.debian.org|https://deb.debian.org|g' {} \; \
    && find /etc/apt/ -name '*.sources' -exec sed -i -e 's|http://deb.debian.org|https://deb.debian.org|g' {} \; \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        gcc \
        libc6-dev \
        libffi-dev \
        netcat-openbsd \
        clamav clamav-daemon clamav-freshclam \
    && rm -rf /var/lib/apt/lists/*

# ADD THIS LINE to ensure /scan exists and is writable
RUN mkdir -p /scan && chmod 777 /scan

# Full python requirements to support development
COPY ./requirements-dev.txt /build/requirements-dev.txt
RUN pip install --no-cache-dir -r requirements-dev.txt

WORKDIR /project
CMD ["/project/dev-docker/django/run.sh"]