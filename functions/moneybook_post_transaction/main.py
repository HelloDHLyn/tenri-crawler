# coding=utf-8

import json
import os
import uuid
from datetime import datetime, timedelta

import boto3


def get_topic_arn(topic_name):
    return "%s:%s" % (os.environ['TOPIC_ARN'], topic_name)


def save_transaction(type, place, price):
    transaction_id = str(uuid.uuid4())
    timestamp = (datetime.now() + timedelta(hours=9)).strftime('%Y-%m-%d %H:%M:%S')

    dynamodb = boto3.client('dynamodb')
    dynamodb.put_item(
        TableName='TenriMoneybook',
        Item={
            'id': {'S': transaction_id},
            'type': {'S': type},
            'place': {'S': place},
            'price': {'N': str(price)},
            'timestamp': {'S': timestamp}
        }
    )

    type_string = '지출' if type == 'EXPENSE' else '수입'
    message = "%s %d원 %s이 등록되었습니다." % (place, price, type_string)

    sns = boto3.client('sns')
    sns.publish(
        TopicArn=get_topic_arn('tenri_send_message'),
        Message=message
    )


def handle(event, context):
    if event['Records']:
        data = json.loads(event['Records'][0]['Sns']['Message'])
        save_transaction(type=data['type'], place=data['place'], price=data['price'])
