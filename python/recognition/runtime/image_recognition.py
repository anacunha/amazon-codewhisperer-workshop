import os
import boto3
import json

sqs = boto3.client("sqs")
rekognition = boto3.client("rekognition")
dynamodb = boto3.client("dynamodb")

queue_url = os.environ["SQS_QUEUE_URL"]
table_name = os.environ["TABLE_NAME"]

# 1.) Detect labels from image with Rekognition
def detect_labels(bucket_name, key):
    response = rekognition.detect_labels(
        Image={
            "S3Object": {
                "Bucket": bucket_name,
                "Name": key
            }
        },
        MaxLabels=10,
        MinConfidence=85
    )
    return response

# 2.) Save labels to DynamoDB
def save_labels_to_db(labels):
    response = dynamodb.put_item(
        TableName=table_name,
        Item=labels
    )

# 3.) Delete message from SQS
def delete_message_from_sqs(receipt_handle):
    sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle
    )


def handler(event, context):
    print(event)
    print(type(event))
    try:
        # process message from SQS
        for Record in event.get("Records"):
            receipt_handle = Record.get("receiptHandle")
            for record in json.loads(Record.get("body")).get("Records"):
                bucket_name = record.get("s3").get("bucket").get("name")
                key = record.get("s3").get("object").get("key")

                # Call function #1 to generate image labels
                labels = detect_labels(bucket_name, key)

                # code snippet to create dynamodb item from labels
                db_result = []
                json_labels = json.dumps(labels["Labels"])
                db_labels = json.loads(json_labels)
                for label in db_labels:
                    db_result.append(label["Name"])
                db_item = {
                    "image": {"S": key},
                    "labels": {"S": str(db_result)}
                }

                # Call function #2 to save labels to DynamoDB
                save_labels_to_db(db_item)

                # Call function #3 to delete message from SQS
                delete_message_from_sqs(receipt_handle)

    except Exception as e:
        print(e)
        print("Error processing object {} from bucket {}. ".format(key, bucket_name))
        raise e
