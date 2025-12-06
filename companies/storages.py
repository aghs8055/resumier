from storages.backends.s3boto3 import S3Boto3Storage


class CompanyLogoStorage(S3Boto3Storage):
    location = 'companies_logo'
    file_overwrite = True
    default_acl = 'private'
