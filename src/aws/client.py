import os
import boto3
from botocore.exceptions import ClientError, BotoCoreError
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

AWS_S3_BUCKET = os.getenv('AWS_S3_BUCKET')
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')

# For Low-Level API calls
s3_client = boto3.client("s3")
# For High-Level API calls
s3_resource = boto3.resource('s3')


def s3_generate_presigned_url(client_method, method_parameters, expires_in=3600):
    """
    Generate a presigned Amazon S3 URL that can be used to perform an action.

    :param client_method: The name of the client method that the URL performs.
    :param method_parameters: The parameters of the specified client method.
    :param expires_in: The number of seconds the presigned URL is valid for.
    :return: The presigned URL.
    """
    try:
        # Enrich the method parameters with the name of the bucket
        method_parameters["Bucket"] = AWS_S3_BUCKET

        url = s3_client.generate_presigned_url(
            ClientMethod=client_method, Params=method_parameters, ExpiresIn=expires_in
        )
        logger.info("Got presigned URL: %s", url)
    except (ClientError, BotoCoreError) as e:
        logger.exception(
            "Couldn't get a presigned URL for client method '%s'.", client_method
        )
        raise
    return url


def s3_list_objects(prefix: str):
    """
    List objects in an Amazon S3 bucket with a specific prefix.

    :param prefix: The prefix of the objects to list.
    :return: The list of objects.
    """
    try:
        if not prefix.endswith("/"):
            prefix += "/"
        objects = s3_client.list_objects_v2(
            Bucket=AWS_S3_BUCKET, Prefix=prefix)
        logger.info("Got objects: %s", objects)
    except (ClientError, BotoCoreError):
        logger.exception("Couldn't list objects with prefix '%s'.", prefix)
        raise
    return objects


def s3_fetch_object_metadata(object):
    try:
        response = s3_client.head_object(
            Bucket=AWS_S3_BUCKET, Key=object['Key'])
        logger.info("Got object metadata: %s", response)
    except (ClientError, BotoCoreError):
        logger.exception("Couldn't get object metadata.")
        raise
    return response
