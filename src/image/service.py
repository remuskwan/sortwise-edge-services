from loguru import logger

import src.aws.client as aws
from src.utils.exceptions import ItemNotFoundError


def get_all_image_metadata():
    pass


def get_image_metadata_by_user_id(user_id: str):
    """Get all images metadata for a user."""
    table = "ImageMetadata"

    try:
        response = aws.dynamo_scan(
            table_name=table,
            FilterExpression='UserId = :user_id',
            ExpressionAttributeValues={
                ':user_id': user_id
            }
        )
        if "Items" not in response:
            raise ItemNotFoundError(
                f"Image with user id {user_id} not found")
    except Exception as err:
        logger.error("Error getting image metadata: {err}", err=err)
        raise
    return response["Items"]


def get_image_metadata_by_object_key(object_key: str):
    """Get a specific inference result."""
    table = "ImageMetadata"
    key = {"ObjectKey": object_key}

    try:
        response = aws.dynamo_get_item(table, key)
        if "Item" not in response:
            raise ItemNotFoundError(
                f"Image with object_key {object_key} not found")
    except Exception as err:
        logger.error("Error getting image metadata: {err}", err=err)
        raise

    return response["Item"]
