import json
from dataclasses import dataclass

from pytest import fixture

from transform_lambda.main import handler


@fixture
def lambda_context():
    @dataclass
    class LambdaContext:
        function_name: str = "test"
        memory_limit_in_mb: int = 128
        invoked_function_arn: str = (
            "arn:aws:lambda:eu-west-1:809313241:function:test"
        )
        aws_request_id: str = "52fdfc07-2182-154f-163f-5f0f9a621d72"

    return LambdaContext()


def test_handler(env, setup_sqs, lambda_context):
    event = {"message": "Hello, World!"}
    response = handler(event, lambda_context)

    assert response == {"statusCode": 200}

