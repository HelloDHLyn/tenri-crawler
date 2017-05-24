# coding=utf-8

import json
import os
from datetime import datetime

import boto3


def get_topic_arn(topic_name):
    return "%s:%s" % (os.environ['TOPIC_ARN'], topic_name)


def get_by_month(transaction_type, month):
    """
    월별 지출 내역을 반환
    """
    dynamodb = boto3.client('dynamodb')

    expression = "#key_type = :value_type AND begins_with(#key_timestamp, :value_timestamp)"
    response = dynamodb.query(
        TableName='TenriMoneybook',
        IndexName='type-timestamp-index',
        KeyConditionExpression=expression,
        ExpressionAttributeNames={
            '#key_type': 'type',
            '#key_timestamp': 'timestamp'
        },
        ExpressionAttributeValues={
            ':value_type': {'S': transaction_type},
            ':value_timestamp': {'S': "%d-%s" % (datetime.now().year, str(month).zfill(2))}
        }
    )

    items = response['Items']
    items.sort(key=lambda x: x['timestamp']['S'])

    price_sum = 0
    for item in items:
        price_sum += int(item['price']['N'])
    message = "%d월 지출 내역이 %d건 있습니다.\n총 지출금액 : %s원" % (month, len(items), "{:,}".format(price_sum))

    sns = boto3.client('sns')
    sns.publish(
        TopicArn=get_topic_arn('tenri_send_message'),
        Message=message
    )


def handle(event, context):
    if event['Records']:
        data = json.loads(event['Records'][0]['Sns']['Message'])
        if data['action'] == 'month':
            get_by_month(data['type'], int(data['month']))

