# AWS Event-Driven Architecture

This project demonstrates an event-driven architecture using AWS services, focusing on EventBridge, SQS, Lambda, Step Functions, and DynamoDB.

## Overview

This pet project showcases the implementation of:
- Amazon EventBridge (Rules and Pipes)
- Amazon Simple Queue Service (SQS) and Dead Letter Queues (DLQ)
- AWS Lambda
- AWS Step Functions
- Amazon DynamoDB

## Project Structure

```
sqs-practice/
├── src/
│   ├── batch_processing_lambda/
│   └── transform_lambda/
├── tests/
│   ├── batch-processing/
│   └── transform-event/
└── infra/
    └── template.yml
```

## Key Components

1. **Transform Lambda**: Processes incoming events and sends them to SQS.
2. **Batch Processing Lambda**: Handles messages from SQS and stores them in DynamoDB.
3. **Infrastructure as Code**: AWS SAM template defining the AWS resources.

## Setup and Deployment

1. Ensure AWS CLI and SAM CLI are installed and configured.
2. Clone the repository and navigate to the project directory.
3. Deploy using SAM:
   ```
   cd infra/
   make deploy
   ```

## Testing

Install required packages.

```
pip install pytest moto
```

Run tests with:
```
pytest tests/batch_processing_lambda/
pytest tests/transform_lambda/
```

