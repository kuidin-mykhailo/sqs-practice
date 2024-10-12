#!/bin/bash

# Укажите имя вашего бакета и путь к файлу
BUCKET_NAME="state-machine-definitions"
LOCAL_FILE_PATH="state_defenition.json"
S3_KEY="state_defenition.json"

# Загрузка файла в S3
aws s3 cp $LOCAL_FILE_PATH s3://$BUCKET_NAME/$S3_KEY
