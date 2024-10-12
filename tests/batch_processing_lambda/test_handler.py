import json
from dataclasses import dataclass

from pytest import fixture

from batch_processing_lambda.main import handler, processor


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


def test_success_handle_sqs_event(env, dynamo_table, lambda_context):
    processor_result = processor
    success_record = {
        "messageId": "message1",
        "body": json.dumps({"Name": "test1"}),
    }
    success_record2 = {
        "messageId": "message2",
        "body": json.dumps({"Name": "test2"}),
    }
    records = {
        "Records": [
            success_record,
            success_record2,
        ]
    }

    res = handler(records, lambda_context)

    assert res == {"batchItemFailures": []}
    assert len(processor_result.fail_messages) == 0
    assert processor_result.success_messages[0] == success_record
    assert processor_result.success_messages[1] == success_record2


def test_failed_handle_half_of_records(env, dynamo_table, lambda_context):
    processor_result = processor
    success_record = {
        "messageId": "message1",
        "body": json.dumps({"Name": "test1"}),
    }
    failed_record = {
        "messageId": "message2",
        "body": json.dumps({"WrongField": "test2"}),
    }
    records = {
        "Records": [
            success_record,
            failed_record,
        ]
    }

    res = handler(records, lambda_context)

    assert res == {
        "batchItemFailures": [{"itemIdentifier": failed_record["messageId"]}]
    }
    assert len(processor_result.fail_messages) == 1
    assert processor_result.success_messages[0] == success_record
