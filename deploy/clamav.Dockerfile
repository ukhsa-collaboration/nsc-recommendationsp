FROM registry.redhat.io/ubi8/ubi

# Install dependencies
RUN dnf install -y epel-release && \
    dnf install -y clamav clamav-update && \
    dnf clean all

# Update ClamAV virus definitions
RUN freshclam

# Expose ClamAV daemon port (optional, if needed)
EXPOSE 3310

# Run ClamAV daemon in foreground
CMD ["clamd", "-F"]
 