import json
import boto3
import logging

logger = logging.getLogger(__name__)

dynamodb = boto3.resource('dynamodb')
iot_client = boto3.client('iot-data', region_name='ap-southeast-1')


def update_image_metadata(object_key, last_modified, inference_results):
    """
    Update the DynamoDB item with the given object_key with inference results.
    :param object_key: The primary key of the item in the DynamoDB table.
    :param inference_results: The inference results to be added to the item.
    """
    table = dynamodb.Table("ImageMetadata")

    try:
        response = table.update_item(
            Key={
                'ObjectKey': object_key,
                "LastModified": last_modified
            },
            UpdateExpression='SET InferenceResults = :val',
            ExpressionAttributeValues={
                ':val': inference_results
            }
        )
        logger.info(
            "InferenceResults for object with key %s updated successfully:", object_key, response)
    except Exception as e:
        print(f"Error updating item: {str(e)}")


def lambda_handler(event, context):
    table = dynamodb.Table('RecyclableItems')

    record = event['Records'][0]
    sns_message = record['Sns']['Message']
    parsed_message = json.loads(sns_message)
    status_code = parsed_message['responsePayload']['statusCode']
    json_body = json.loads(parsed_message['responsePayload']['body'])

    # Only process if there is no errors
    if status_code != 200:
        return {
            'statusCode': 400,
            'body': {
                "Error": json_body['Error'],
                "ErrorMessage": json_body['ErrorMessage']
            }
        }

    labels = json_body["Labels"]
    print(f'Labels: {labels}')

    object_key = json_body["Object_key"]
    last_modified = json_body["Last_modified"]

    try:
        for label_1 in labels:
            for label_2 in labels[1:]:
                db_response = table.get_item(
                    Key={
                        'ItemType': label_1['Name'],
                        'MaterialType': label_2['Name']
                    }
                )
                if 'Item' not in db_response:
                    db_response = table.get_item(
                        Key={
                            'ItemType': label_2['Name'],
                            'MaterialType': label_1['Name']
                        }
                    )
                if 'Item' in db_response:
                    results = db_response['Item']
                    print(f"Found item: {results}")

                    iot_response = iot_client.publish(
                        topic='inference/results',
                        qos=1,
                        payload=json.dumps(results)
                    )

                    # enrich image metadata with inference results
                    update_image_metadata(object_key, last_modified, results)

                    return {
                        'statusCode': 200,
                        'body': json.dumps('Processed labels and queried DynamoDB.')
                    }
    except Exception as err:
        lambda_response = {
            'statusCode': 400,
            'body': {
                "Error": str(err)
            }
        }
        return lambda_response
