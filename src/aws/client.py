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
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION')

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_DEFAULT_REGION
)

# For Low-Level API calls
s3_client = session.client("s3")
# For High-Level API calls
s3_resource = session.resource('s3')
dynamo_resource = session.resource('dynamodb')


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
        logger.info("Got presigned URL: {url}", url=url)
    except (ClientError, BotoCoreError) as e:
        logger.exception(
            "Couldn't get a presigned URL for action '{action}'.", action=client_method
        )
        raise
    return url


def s3_fetch_object_metadata(object):
    try:
        response = s3_client.head_object(
            Bucket=AWS_S3_BUCKET, Key=object['Key'])
        logger.info("Got object metadata for key {key}", key=object['Key'])
    except (ClientError, BotoCoreError):
        logger.exception("Couldn't get object metadata.")
        raise
    return response


def dynamo_query_item(table_name: str, **kwargs):
    """
    Get an item from a DynamoDB table.
    :param table_name: The name of the table.
    :param key: The key of the item to get.
    :return: The item.
    """
    try:
        table = dynamo_resource.Table(table_name)
        response = table.query(**kwargs)
        logger.info("Got item: {item}", item=response)
    except (ClientError, BotoCoreError):
        logger.exception(
            "Couldn't get item from table '{table_name}'.", table_name=table_name)
        raise
    return response


def dynamo_scan(table_name: str, **kwargs):
    try:
        table = dynamo_resource.Table(table_name)
        response = table.scan(**kwargs)
    except (ClientError, BotoCoreError):
        logger.exception(
            "Couldn't scan table '{table_name}'.", table_name=table_name)
        raise
    return response
