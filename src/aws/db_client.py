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

# For High-Level API calls
db_resource = boto3.resource('dynamodb', region_name=AWS_DEFAULT_REGION)


def dynamo_get_item(table_name: str, key: dict):
    """
    Get an item from a DynamoDB table.
    :param table_name: The name of the table.
    :param key: The key of the item to get.
    :return: The item.
    """
    try:
        table = db_resource.Table(table_name)
        response = table.get_item(Key=key)
        logger.info("Got item: {item}", item=response)
    except (ClientError, BotoCoreError):
        logger.exception(
            "Couldn't get item from table '{table_name}'.", table_name=table_name)
        raise
    return response
