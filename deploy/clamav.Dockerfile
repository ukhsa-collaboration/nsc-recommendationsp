FROM clamav/clamav:1.4.3

# Fix permissions for OpenShift
RUN chgrp -R 0 /var/lib/clamav && chmod -R g=u /var/lib/clamav
RUN chgrp -R 0 /var/log/clamav && chmod -R g=u /var/log/clamav

# Set ownership so non-root user 1001 can write
RUN chown -R 1001:0 /var/lib/clamav && chmod 775 /var/lib/clamav
RUN chown -R 1001:0 /var/log/clamav && chmod 775 /var/log/clamav

# Create the wrapper script to update virus definitions at container start
USER 0
RUN echo '#!/bin/sh\n\
echo "[INIT] Updating virus definitions..."\n\
freshclam || echo "[WARNING] freshclam failed"\n\
exec /init-unprivileged "$@"' > /entrypoint.sh && chmod +x /entrypoint.sh

# Switch to non-root user
USER 1001

# Use the wrapper as the entrypoint
ENTRYPOINT ["/entrypoint.sh"]