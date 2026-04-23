FROM quay.io/sclorg/postgresql-15-c9s

USER 0
RUN python3 -m ensurepip --upgrade \
    && python3 -m pip install --no-cache-dir --upgrade pip \
    && python3 -m pip install --no-cache-dir boto3==1.38.30

COPY backup.py /usr/local/bin/backup.py
COPY apply_lifecycle.py /usr/local/bin/apply_lifecycle.py
COPY list_bucket.py /usr/local/bin/list_bucket.py
COPY restore_verify.py /usr/local/bin/restore_verify.py
COPY restore_helper.py /usr/local/bin/restore_helper.py
RUN chmod 0755 /usr/local/bin/backup.py /usr/local/bin/apply_lifecycle.py \
    /usr/local/bin/list_bucket.py /usr/local/bin/restore_verify.py \
    /usr/local/bin/restore_helper.py

USER 26
ENV PYTHONDONTWRITEBYTECODE=1
ENTRYPOINT ["/usr/local/bin/backup.py"]
