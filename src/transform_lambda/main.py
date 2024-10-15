from datetime import datetime
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.parser import BaseModel, Field, ValidationError
from botocore.exceptions import ClientError

logger = Logger()


class Message(BaseModel):
    message: str = Field(..., alias="Message")
    transformed_at: datetime = Field(
        default_factory=datetime.utcnow, alias="transformedAt"
    )


def transform_message(message: str):
    """
    Swap case of the message
    """
    return message.swapcase()


def process_event(event: dict) -> dict:
    try:
        message = Message.parse_obj(event)
        message.message = transform_message(message.message)
        logger.info("Sending message to Batching SQS")
        return message.json(by_alias=True)
    except (ValidationError, ClientError) as e:
        logger.exception("Error transforming message")
        raise e


@logger.inject_lambda_context(log_event=True)
def handler(event, context: LambdaContext):
    if isinstance(event, dict):
        # sqs_client = get_sqs_client()
        body = event["parsedBody"]["data"]
        transformed_data = process_event(body)
    else:
        logger.error("Event must be a dictionary. Sending to DLQ.")
        # send_to_sqs(sqs_client, os.environ["DLQ_URL"], json.dumps(event))
        # Better to return error and handle DLQ forwarding as separate step in StateMachine
    return {"statusCode": 200, "body": transformed_data}
