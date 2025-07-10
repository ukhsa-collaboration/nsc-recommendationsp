FROM docker.io/clamav/clamav:1.4.3

# Make group 0 the owner and set group permissions (root can write)
RUN chgrp -R 0 /var/lib/clamav && chmod -R g=u /var/lib/clamav
RUN chgrp -R 0 /var/log/clamav && chmod -R g=u /var/log/clamav
# Run freshclam as root (default user) with write access to /var/lib/clamav
RUN freshclam
# Change ownership to non-root user (1001)
RUN chown -R 1001:0 /var/lib/clamav && chmod 775 /var/lib/clamav
RUN chown -R 1001:0 /var/log/clamav && chmod 775 /var/log/clamav

USER 1001

ENTRYPOINT ["/bin/sh", "/init-unprivileged"]