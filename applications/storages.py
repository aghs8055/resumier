from storages.backends.s3boto3 import S3Boto3Storage


class ResumeStorage(S3Boto3Storage):
    location = 'application/resume'
    overwrite = False
    default_acl = 'private'
