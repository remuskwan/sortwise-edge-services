from loguru import logger

from aws.client import dynamo_get_item
from utils.exceptions import ItemNotFoundError


def get_image_metadata_by_object_key(object_key: str):
    """Get a specific inference result."""
    table = "ImageMetadata"
    key = {"ObjectKey": object_key}

    try:
        response = dynamo_get_item(table, key)
        if "Item" not in response:
            raise ItemNotFoundError(
                f"Image with object_key {object_key} not found")
    except Exception as err:
        logger.error("Error getting image metadata: {err}", err=err)
        raise

    return response["Item"]
