FROM node:12.14.1-slim

# Default to watching
# Override with:
#   docker run -e NPM_ENV=dev container_name
ENV STATIC_MODE watch

# Leave the entrypoint to npm install each time, so it goes into the project volume
CMD ["/project/containers/static/run.sh"]
