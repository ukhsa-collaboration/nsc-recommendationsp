from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    """
    Storage settings for uploaded files.

    Since static files are served by whitenoise we could have just defined the
    AWS_LOCATION, AWS_S3_FILE_OVERWRITE settings however defining a custom
    storage is cleaner if any other storage options are defined in the future.
    """

    location = "media"
    file_overwrite = False
