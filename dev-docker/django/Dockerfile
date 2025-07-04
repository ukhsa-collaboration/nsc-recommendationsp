FROM python:3.12-slim

RUN mkdir /build
WORKDIR /build

# Build process dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    postgresql-client \
    gcc \
    libc6-dev \
    libffi-dev \
    netcat-openbsd \
    clamav clamav-daemon clamav-freshclam \
    && rm -rf /var/lib/apt/lists/*

# Full python requirements to support development
COPY ./requirements-dev.txt /build/requirements-dev.txt
RUN pip install --no-cache-dir -r requirements-dev.txt
# Run Django
WORKDIR /project
CMD ["/project/dev-docker/django/run.sh"]