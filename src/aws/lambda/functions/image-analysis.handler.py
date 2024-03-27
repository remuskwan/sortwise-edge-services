import json
import logging
import boto3

from botocore.exceptions import ClientError
from datetime import datetime
from os import environ

# Set up logging.
logger = logging.getLogger(__name__)

# Get the model confidence and max labels.
min_confidence = int(environ.get('CONFIDENCE', 50))
max_labels = int(environ.get('MAX_LABELS', 10))

# Get the boto3 client
s3 = boto3.client('s3')
rek_client = boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb')


def persist_image_metadata(record, metadata):
    table = dynamodb.Table('ImageMetadata')

    bucket_name = record['s3']['bucket']['name']
    object_key = record['s3']['object']['key']
    last_modified = metadata.get('LastModified', datetime.utcnow())
    last_modified = last_modified.isoformat()
    size = metadata.get('ContentLength', 0)
    content_type = metadata.get('ContentType', "")

    parts = object_key.split('/')
    user_id, file_name = parts[0], parts[-1]

    try:
        item = {
            'ObjectKey': object_key,
            'LastModified': last_modified,
            'BucketName': bucket_name,
            'FileName': file_name,
            'FileSize': size,
            "ContentType": content_type
        }
        if user_id != "general":
            item["UserId"] = user_id
        # If object key exists in table, update the item instead of creating a new one
        response = table.put_item(Item=item)
    except ClientError as e:
        logger.error("Error processing record %s:", str(e))
        raise
    except Exception as e:
        logger.error("Unexpected error processing record %s: %s",
                     record, str(e))
        raise

    return {'LastModified': last_modified}


def get_s3_object_metadata(record):
    table = dynamodb.Table('ImageMetadata')

    bucket_name = record['s3']['bucket']['name']
    object_key = record['s3']['object']['key']
    try:
        response = s3.head_object(Bucket=bucket_name, Key=object_key)
    except ClientError as e:
        logger.error("Error getting object metadata %s:", str(e))
        raise
    except Exception as e:
        logger.error(
            "Unexpected error getting object metadata %s: %s", record, str(e))
        raise
    return response


def lambda_handler(event, context):
    """
    Lambda handler function
    param: event: The event object for the Lambda function.
    param: context: The context object for the lambda function.
    return: The labels found in the image passed in the event
    object.
    """

    try:
        record = event['Records'][0]

        # Get S3 object metadata
        image_metadata = get_s3_object_metadata(record)
        # Write to DynamoDB
        persist_resp = persist_image_metadata(record, image_metadata)
        last_modified = persist_resp['LastModified']

        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        image = {'S3Object':
                 {'Bucket':  bucket,
                  'Name': key}
                 }

        # Analyze the image.
        response = rek_client.detect_labels(Image=image,
                                            MaxLabels=max_labels,
                                            MinConfidence=min_confidence)

        # Get the custom labels
        labels = response['Labels']

        lambda_response = {
            "statusCode": 200,
            "body": json.dumps({
                "Labels": labels,
                "Object_key": key,
                "Last_modified": last_modified
            })
        }

    except ClientError as err:
        error_message = f"Couldn't analyze image. " + \
            err.response['Error']['Message']

        lambda_response = {
            'statusCode': 400,
            'body': {
                "Error": err.response['Error']['Code'],
                "ErrorMessage": error_message
            }
        }
        logger.error("Error function %s: %s",
                     context.invoked_function_arn, error_message)

    except ValueError as val_error:
        lambda_response = {
            'statusCode': 400,
            'body': {
                "Error": "ValueError",
                "ErrorMessage": format(val_error)
            }
        }
        logger.error("Error function %s: %s",
                     context.invoked_function_arn, format(val_error))

    return lambda_response
