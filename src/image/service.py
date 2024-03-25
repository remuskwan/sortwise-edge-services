from loguru import logger

from src.aws.client import dynamo_get_item
from src.utils.exceptions import ItemNotFoundError


def get_all_image_metadata():
    pass


def get_all_image_metadata_for_user(user_id: str):
    """Get all images metadata for a user."""
    table = "ImageMetadata"
    key = {"UserId": user_id}
    pass


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
