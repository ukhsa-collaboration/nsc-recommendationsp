FROM docker.io/clamav/clamav:1.4.3

# Make group 0 the owner and set group permissions (root can write)
RUN chgrp -R 0 /var/lib/clamav && chmod -R g=u /var/lib/clamav
RUN chgrp -R 0 /var/log/clamav && chmod -R g=u /var/log/clamav

# Change ownership to non-root user (1001)
RUN chown -R 1001:0 /var/lib/clamav && chmod 775 /var/lib/clamav
RUN chown -R 1001:0 /var/log/clamav && chmod 775 /var/log/clamav

# Create the wrapper script to update virus definitions at container start
USER 0

RUN sh -c 'cat << "EOF" > /entrypoint-clamav.sh
#!/bin/sh
echo "[INIT] Updating virus definitions..."
freshclam || echo "[WARNING] freshclam failed"
exec /init-unprivileged "$@"
EOF' && chmod +x /entrypoint-clamav.sh

# Switch to non-root user
USER 1001
# Use the wrapper as the entrypoint
ENTRYPOINT ["/entrypoint-clamav.sh"]