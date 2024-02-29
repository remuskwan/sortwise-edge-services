import os
import boto3
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

AWS_S3_BUCKET = os.getenv('AWS_S3_BUCKET')
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')

# Create S3 client
s3 = boto3.resource('s3')


async def s3_upload(contents: bytes, key: str):
    logger.info(f'Uploading {key} to s3')
    s3.Bucket(AWS_S3_BUCKET).put_object(Key=key, Body=contents)
