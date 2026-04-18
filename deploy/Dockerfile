#
# Build the backend image (incorporating the output from FRONT_END_BUILD)
#

#
# NOTE: Requires the compiled static from the frontend to be built
#       This is handled in openshift
#

FROM python:3.13-slim

USER root

ENV SHELL=/bin/bash \
    SRC_ROOT=/opt/app-root/src/ \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

RUN mkdir -p $SRC_ROOT
WORKDIR $SRC_ROOT

# Install uv (package manager) via pip (bootstrap only).
RUN pip install --no-cache-dir uv==0.9.22

# Resolve prod dependencies from the lockfile. Cached as long as
# pyproject.toml + uv.lock are unchanged.
COPY pyproject.toml uv.lock $SRC_ROOT
RUN uv sync --frozen --no-dev --no-install-project

# Copy the source and finalise install (includes the project itself).
COPY . $SRC_ROOT
RUN uv sync --frozen --no-dev

# Put the venv on PATH so entrypoint.sh / gunicorn / python resolve
# to the .venv binaries without needing a "uv run" prefix.
ENV PATH="${SRC_ROOT}.venv/bin:${PATH}"

RUN DJANGO_CONFIGURATION=Build python manage.py collectstatic --noinput

ENTRYPOINT ["./deploy/entrypoint.sh"]
CMD ["gunicorn", "-c", "gunicorn.conf.py", "nsc.wsgi"]

# setup the container user so that is can be ran by an arbitrary user
# https://docs.openshift.com/container-platform/3.3/creating_images/guidelines.html#openshift-container-platform-specific-guidelines
RUN chgrp -R 0 ${SRC_ROOT}.. && \
    chmod -R g=u ${SRC_ROOT}..

USER 1001
