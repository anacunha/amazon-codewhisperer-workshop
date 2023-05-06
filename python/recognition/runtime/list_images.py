import os
import boto3
import json

table_name = os.environ["TABLE_NAME"]

# 1.)


def handler(event, context):

    #


    return {
        "body": json.dumps(response),
        "statusCode": 200
    }
