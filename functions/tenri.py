# coding=utf-8

import os
import re
import json

import boto3

sns = boto3.client('sns')


def get_topic_arn(topic_name):
    return "%s:%s" % (os.environ['TOPIC_ARN'], topic_name)


def send_message(message):
    sns.publish(
        TopicArn=get_topic_arn('tenri_send_message'),
        Message=message
    )


def parse_moneybook(text):
    """
    가계부 명령어 파싱
    """

    # 지출
    result = re.search(ur'(?P<place>[가-힣a-zA-Z\d\s]+) (?P<price>\d+)원 지출', text, re.UNICODE)
    if result:
        place = result.group('place')  # 사용처
        price = int(result.group('price'))  # 금액
        json_data = json.dumps({
            'type': 'EXPENSE',
            'place': place,
            'price': int(price)
        })

        sns.publish(
            TopicArn=get_topic_arn('tenri_moneybook_post_transaction'),
            Message=json_data
        )

        exit()


def handler(event, context):
    chat_id = str(event['message']['from']['id'])
    if chat_id != os.environ['TELEGRAM_ID']:
        exit()

    # 테스트 메시지
    text = event['message']['text']
    if text.strip() == "테스트":
        send_message("테스트 메시지입니다.")
        exit()

    parse_moneybook(text)

    send_message("'%s' 명령을 인식하지 못했습니다." % text)
