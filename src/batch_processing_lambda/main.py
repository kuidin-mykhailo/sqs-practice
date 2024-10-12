import os
from functools import lru_cache
from uuid import uuid4

import boto3
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.batch import (
    BatchProcessor,
    EventType,
    process_partial_response,
)
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord
from aws_lambda_powertools.utilities.typing import LambdaContext
from botocore.exceptions import ClientError
from mypy_boto3_dynamodb import DynamoDBClient
from pydantic import BaseModel, Field

processor = BatchProcessor(event_type=EventType.SQS)
logger = Logger()


@lru_cache
def get_dynamo_client(region_name: str = "eu-central-1") -> DynamoDBClient:
    return boto3.client("dynamodb", region_name=region_name)


class MyData(BaseModel):
    batch_id: str = Field(str(uuid4()))
    name: str = Field(..., alias="Name")

    def as_dynamo_item(self):
        return {
            "BatchId": {"S": self.batch_id},
            "Name": {
                "S": self.name,
            },
        }


# It could be a DynamoClient class which stores:
# - Metadata data about Dynamo Table
# - DynamoClient
# - Support PutItem based on `as_dynamo_item`.
def store_record(client: DynamoDBClient, data: MyData):
    try:
        client.put_item(
            TableName=os.environ["DYNAMO_TABLE"], Item=data.as_dynamo_item()
        )
        logger.info("Item %s stored in Table", data)
    except ClientError as e:
        logger.error("An error raised during PutItem in Table: %s", e)
        raise e


def record_handler(record: SQSRecord):
    payload = MyData.model_validate(record.json_body)
    logger.info(payload)
    dynamo_client = get_dynamo_client()
    # TODO: make it async
    store_record(dynamo_client, payload)


def handler(event, context: LambdaContext):
    return process_partial_response(
        event=event,
        record_handler=record_handler,
        processor=processor,
        context=context,
    )
