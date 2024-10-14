import pytest
from botocore.exceptions import ClientError
from conftest import TEST_TABLE_NAME
from moto import mock_aws

from batch_processing_lambda.main import (
    MyData,
    get_dynamo_client,
    store_record,
)


def test_store_record_success(env, dynamo_table):
    dynamo_client = get_dynamo_client()

    test_data = MyData(Message="TestName", transformedAt="2012-06-20")

    store_record(dynamo_client, test_data)
    response = dynamo_client.get_item(
        TableName=TEST_TABLE_NAME, Key={"BatchId": {"S": test_data.batch_id}}
    )

    assert "Item" in response
    item = response["Item"]
    assert item["Message"]["S"] == "TestName"


@mock_aws
def test_store_failed_raise_an_error(env, monkeypatch):
    dynamo_client = get_dynamo_client()

    test_data = MyData(Message="Failed", transformedAt="2012-06-20")

    def mock_put_item(*args, **kwargs):
        raise ClientError({"Error": {"Code": "TestError"}}, "PutItem")

    monkeypatch.setattr(dynamo_client, "put_item", mock_put_item)

    with pytest.raises(ClientError) as error:
        store_record(dynamo_client, test_data)

    assert error.value.response["Error"]["Code"] == "TestError"
