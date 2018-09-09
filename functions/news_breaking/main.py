import json
import os

import boto3
import twitter
from botocore.vendored.requests.packages import urllib3

http = urllib3.PoolManager()

# 연합뉴스 유저 ID
USER_ID = 147451838


def get_last_id():
    res = http.request('GET', 'https://api.lynlab.co.kr/v1/key_values/TENRI_NEWS_LAST_ID',
                       headers={'x-api-key': os.environ['LYNLAB_API_KEY']})

    if res.status == 200:
        return int(json.loads(res.data.decode('utf-8'))['value'])
    else:
        raise RuntimeError


def set_last_id(last_id):
    data = {'key': 'TENRI_NEWS_LAST_ID', 'value': str(last_id)}
    http.request('POST',
                 'https://api.lynlab.co.kr/v1/key_values',
                 body=json.dumps(data).encode('utf-8'),
                 headers={'x-api-key': os.environ['LYNLAB_API_KEY']})


def send_message(message):
    sqs = boto3.client('sqs')

    queue_url = sqs.get_queue_url(QueueName='lynlab-tenri-discord')['QueueUrl']
    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps({
            'channel_name': 'breaking',
            'content': '속보가 도착했습니다.',
            'embed': {
                'title': '본문',
                'description': message,
            },
        }, ensure_ascii=False),
    )


def handle(event, context):
    api = twitter.Api(consumer_key=os.environ['CONSUMER_KEY'],
                      consumer_secret=os.environ['CONSUMER_SECRET'],
                      access_token_key=os.environ['ACCESS_TOKEN_KEY'],
                      access_token_secret=os.environ['ACCESS_TOKEN_SECRET'])

    statuses = api.GetUserTimeline(user_id=USER_ID, since_id=get_last_id(), include_rts=False, exclude_replies=True)
    for status in reversed(statuses):
        if '속보' in status.text or '1보' in status.text:
            send_message(status.text)

    if len(statuses) > 0:
        set_last_id(statuses[0].id)
