import os
import sys
from pathlib import Path

import boto3
from moto import mock_aws
from pytest import fixture

project_root = Path(__file__).parent.parent.parent

src_path = os.path.join(project_root, "src")
sys.path.insert(0, str(src_path))

lambda_path = os.path.join(src_path, "transform_lambda")
sys.path.insert(0, str(lambda_path))

TEST_SQS_URL = "test-queue"
TEST_DLQ_URL = "test-dlq"

@fixture
def env():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["SQS_URL"] = TEST_SQS_URL
    os.environ["DLQ_URL"] = TEST_DLQ_URL


@fixture
def setup_sqs():
    with mock_aws():
        sqs_client = boto3.client("sqs", region_name="eu-central-1")
        sqs_client.create_queue(QueueName=TEST_SQS_URL)
        sqs_client.create_queue(QueueName=TEST_DLQ_URL)
        yield
