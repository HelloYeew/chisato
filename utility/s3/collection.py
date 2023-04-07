import boto3
from decouple import config

S3_COLLECTION_REGION_NAME = config('S3_COLLECTION_REGION_NAME', default='')
S3_COLLECTION_ENDPOINT_URL = config('S3_COLLECTION_ENDPOINT_URL', default='')
S3_COLLECTION_ACCESS_KEY_ID = config('S3_COLLECTION_ACCESS_KEY_ID', default='')
S3_COLLECTION_SECRET_ACCESS_KEY = config('S3_COLLECTION_SECRET_ACCESS_KEY', default='')


def get_collection_s3_client():
    """Get s3 client for collection bucket."""
    session = boto3.session.Session()

    return session.client(
        's3',
        region_name=S3_COLLECTION_REGION_NAME,
        endpoint_url=S3_COLLECTION_ENDPOINT_URL,
        aws_access_key_id=S3_COLLECTION_ACCESS_KEY_ID,
        aws_secret_access_key=S3_COLLECTION_SECRET_ACCESS_KEY
    )
