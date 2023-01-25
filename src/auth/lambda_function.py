import logging
import os

import boto3


logger = logging.getLogger()
logger.setLevel("INFO")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def lambda_handler(event, context):
    logger.info(event)
    try:
        item = table.get_item(Key={"key": event["authorizationToken"]})["Item"]
    except Exception:
        logger.exception("authorizationToken is not exist in auth table.")
        return {
            "principalId": "yyyyyyyy",
            "policyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": "*",
                        "Effect": "Deny",
                        "Resource": "*",
                    }
                ]
            }
        }
    return {
        "principalId": "yyyyyyyy",
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Allow",
                    "Resource": f"arn:aws:execute-api:{os.environ['REGION']}:{os.environ['ACCOUNT_ID']}:*/*/POST/usr/{item['id']}"
                }
            ]
        }
    }
