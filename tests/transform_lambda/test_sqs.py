import json

import pytest
from botocore.exceptions import ClientError
from moto import mock_aws

from transform_lambda.main import Message, get_sqs_client, send_to_sqs


@pytest.mark.parametrize(
    "message",
    ["abc", {"message": "abc"}, Message(message="abc").model_dump_json()],
)
def test_success_put_message_into_sqs(env, setup_sqs, message):
    sqs_client = get_sqs_client()
    send_to_sqs(sqs_client, "test-queue", message)
    response = sqs_client.receive_message(QueueUrl="test-queue")
    assert response["Messages"][0]["Body"] == message


@mock_aws
def test_catch_exception_when_put_message_into_sqs(env, monkeypatch):
    sqs_client = get_sqs_client()

    def mock_send_message(*args, **kwargs):
        raise ClientError(
            {"Error": {"Code": "TestError", "Message": "TestMessage"}},
            "SendMessage",
        )

    monkeypatch.setattr(sqs_client, "send_message", mock_send_message)

    with pytest.raises(ClientError) as e:
        send_to_sqs(sqs_client, "test-queue", "abc")

    assert e.value.response["Error"]["Code"] == "TestError"
    assert e.value.response["Error"]["Message"] == "TestMessage"
