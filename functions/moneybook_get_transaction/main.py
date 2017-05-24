# coding=utf-8

import json
import os
from datetime import datetime

import boto3


def get_topic_arn(topic_name):
    return "%s:%s" % (os.environ['TOPIC_ARN'], topic_name)


def get_by_month(month):
    """
    월별 지출 내역을 반환
    """

    def query(transaction_type):
        dynamodb = boto3.client('dynamodb')
        expression = "#key_type = :value_type AND begins_with(#key_timestamp, :value_timestamp)"

        return dynamodb.query(
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

    expenses = list(filter(lambda i: i['type']['S'] == 'EXPENSE', query('EXPENSE')['Items']))
    incomes = list(filter(lambda i: i['type']['S'] == 'INCOME', query('INCOME')['Items']))

    expense_sum = sum(map(lambda i: int(i['price']['N']), expenses))
    income_sum = sum(map(lambda i: int(i['price']['N']), incomes))

    message = "%d월 지출 %d건, 소득 %d건의 내역이 있습니다.\n\n" \
              "소득 : %s원\n" \
              "지출 : %s원\n" \
              "순이익 : %s원\n" \
              % (month, len(expenses), len(incomes),
                 "{:,}".format(expense_sum), "{:,}".format(income_sum), "{:,}".format(income_sum - expense_sum))

    sns = boto3.client('sns')
    sns.publish(
        TopicArn=get_topic_arn('tenri_send_message'),
        Message=message
    )


def handle(event, context):
    if event['Records']:
        data = json.loads(event['Records'][0]['Sns']['Message'])
        if data['action'] == 'month':
            get_by_month(int(data['month']))

