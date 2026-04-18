FROM quay.io/sclorg/postgresql-15-c9s

USER 0
RUN python3 -m ensurepip --upgrade \
    && python3 -m pip install --no-cache-dir --upgrade pip \
    && python3 -m pip install --no-cache-dir boto3==1.38.30

COPY backup.py /usr/local/bin/backup.py
RUN chmod 0755 /usr/local/bin/backup.py

USER 26
ENTRYPOINT ["/usr/local/bin/backup.py"]
