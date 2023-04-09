import boto3
from decouple import config

S3_STATIC_BUCKET_NAME = config('S3_STATIC_BUCKET_NAME', default='')
S3_STATIC_REGION_NAME = config('S3_STATIC_REGION_NAME', default='')
S3_STATIC_ENDPOINT_URL = config('S3_STATIC_ENDPOINT_URL', default='')
S3_STATIC_ACCESS_KEY_ID = config('S3_STATIC_ACCESS_KEY_ID', default='')
S3_STATIC_SECRET_ACCESS_KEY = config('S3_STATIC_SECRET_ACCESS_KEY', default='')
S3_STATIC_URL = config('S3_STATIC_URL', default='')
USE_DIGITALOCEAN_SPACES= config('USE_DIGITALOCEAN_SPACES', default=False, cast=bool)


def get_static_s3_client():
    """Get s3 client for static file bucket."""
    session = boto3.session.Session()

    return session.client(
        's3',
        region_name=S3_STATIC_REGION_NAME,
        endpoint_url=S3_STATIC_ENDPOINT_URL,
        aws_access_key_id=S3_STATIC_ACCESS_KEY_ID,
        aws_secret_access_key=S3_STATIC_SECRET_ACCESS_KEY
    )


def generate_static_url(path: str) -> str:
    """Generate static url from the path using the static URL from the config."""
    # if path start with /, remove it
    if path.startswith('/'):
        path = path[1:]
    if USE_DIGITALOCEAN_SPACES:
        # Don't know is this a bug or not but digital ocean will add bucket name as primary folder name
        base_url = S3_STATIC_URL + "/" + S3_STATIC_BUCKET_NAME + "/" + path
    else:
        base_url = S3_STATIC_URL + "/" + path
    return base_url
