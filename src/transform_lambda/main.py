import json
import os
from datetime import datetime
from functools import lru_cache

import boto3
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.parser import BaseModel, Field, ValidationError
from botocore.exceptions import ClientError
from mypy_boto3_sqs import SQSClient

logger = Logger()


class Message(BaseModel):
    message: str = Field(..., alias="Message")
    transformed_at: datetime = Field(
        default_factory=datetime.utcnow, alias="transformedAt"
    )


@lru_cache
def get_sqs_client(region_name: str = "eu-central-1") -> SQSClient:
    return boto3.client("sqs", region_name=region_name)


def transform_message(message: str):
    """
    Swap case of the message
    """
    return message.swapcase()


def send_to_sqs(sqs_client: SQSClient, sqs_url: str, message: str):
    """
    Send message to SQS

    Args:
        sqs_client (SQSClient): SQS client
        sqs_url (str): SQS URL
        message (str): Message to send. JSON string.
    """
    try:
        sqs_client.send_message(
            QueueUrl=sqs_url,
            MessageBody=message,
        )
    except ClientError as e:
        logger.exception("Error sending message to SQS")
        raise e


def process_event(sqs_client: SQSClient, event: dict):
    try:
        message = Message.model_validate(event)
        message.message = transform_message(message.message)
        logger.info("Sending message to Batching SQS")
        send_to_sqs(
            sqs_client, os.environ["SQS_URL"], message.model_dump_json(by_alias=True)
        )
    except (ValidationError, ClientError):
        logger.exception("Error transforming message")
        send_to_sqs(sqs_client, os.environ["DLQ_URL"], json.dumps(event))
        logger.info(f"Message sent to DLQ: {event}")


def handler(event, context):
    logger.info("Input event: %s", event)
    if isinstance(event, dict):
        sqs_client = get_sqs_client()
        body = json.loads(event["body"])
        process_event(sqs_client, body)
    else:
        logger.error("Event must be a dictionary. Sending to DLQ.")
        send_to_sqs(sqs_client, os.environ["DLQ_URL"], json.dumps(event))
        # Better to return error and handle DLQ forwarding as separate step in StateMachine
    return {"statusCode": 200}
