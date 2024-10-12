import os
import sys
from pathlib import Path

import boto3
from moto import mock_aws
from pytest import fixture

project_root = Path(__file__).parent.parent.parent

src_path = os.path.join(project_root, "src")
sys.path.insert(0, str(src_path))

lambda_path = os.path.join(src_path, "batching_processing_lambda")
sys.path.insert(0, str(lambda_path))

TEST_TABLE_NAME = "TestingTable"


@fixture
def env():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["DYNAMO_TABLE"] = TEST_TABLE_NAME


@fixture
def dynamo_table():
    with mock_aws():
        dynamodb = boto3.client("dynamodb", region_name="eu-central-1")
        dynamodb.create_table(
            TableName=TEST_TABLE_NAME,
            KeySchema=[
                {"AttributeName": "BatchId", "KeyType": "HASH"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "BatchId", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        yield
