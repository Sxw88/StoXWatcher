#!/usr/bin/python3

# This script uses the Telegram Bot API to send updates 
# to a group with the specified chat_id

import requests
import sys

# Get the token for Telegram Bot
with open('conf/telg_token', 'r') as token_file:
    telg_token = token_file.read()
    telg_token = telg_token[:-1]

# Get the Telegram Chat ID
with open('conf/telg_chatid', 'r') as chatid_file:
    telg_chat_id = chatid_file.read()
    telg_chat_id = telg_chat_id[:-1]

telg_method  = 'sendMessage'


def sendMessage(text_data, _token=telg_token, _method=telg_method, _chat_id=telg_chat_id):

    response = requests.post(
            url='https://api.telegram.org/bot{0}/{1}'.format(_token,_method),
            data={'chat_id': _chat_id, 'text': text_data}
        ).json()

    print(response)



