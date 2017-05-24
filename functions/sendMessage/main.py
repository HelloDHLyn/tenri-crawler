# coding=utf-8

import os
import urllib
import urllib2


def handle(event, context):
    text = event['Records'][0]['Sns']['Message']
    data = {
        'chat_id': os.environ['CHAT_ID'],
        'text': text,
        'parse_mode': 'HTML'
    }

    request = urllib2.Request(os.environ['TENRI_BOT_URL'] + '/sendMessage', data=urllib.urlencode(data))
    urllib2.urlopen(request)
