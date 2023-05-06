import os
import boto3
import json

table_name = os.environ["TABLE_NAME"]

# 1.) Function to list all items from a DynamoDB table

def list_items():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    response = table.scan()
    return response['Items']

def handler(event, context):

    # Call function #1 to scan items from DynamoDB table
    response = list_items()

    return {
        "body": json.dumps(response),
        "statusCode": 200
    }
