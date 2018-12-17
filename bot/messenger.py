import json, requests, random, re
from pprint import pprint
from bot import nlpluisai
import wikipedia
from word2number.w2n import word_to_num
from bot.models import *
from datetime import datetime
from .intents_replies import intents, none_reply
from bot.dialogflow import get_response

PAGE_ACCESS_TOKEN = "EAACwSutJ0Q8BAC42dpG0pfwrThBVFKzehsxLGNd7RsewBdA5TheMOZCfW6HtXQxrxaGPa8zdLHtZAvuWdLz7mvTRx926vf1ZB0uXcp2iz2O12NHVRdNlb1GsZANDJ2uBW88BqMVtCQxBwN4lY67jdPFh1Ce1PSdE4EhZAU9zE7mTOznA3psN5"


def get_user(fbid):
    try:
        if MessengerUser.objects.filter(id=fbid).count() == 0:
            user_details_url = "https://graph.facebook.com/v2.6/%s" % fbid
            user_details_params = {'fields': 'id,first_name,last_name,email', 'access_token': PAGE_ACCESS_TOKEN}
            user_details = requests.get(user_details_url, user_details_params).json()
            user = MessengerUser(**user_details)
            user.save()
        else:
            user = MessengerUser.objects.get(id=fbid)
        return user
    except Exception as es:
        return None
        pass


def send_message(fbid, text, **kwargs):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s' % PAGE_ACCESS_TOKEN
    response_msg = json.dumps({"recipient": {"id": fbid}, "message": {"text": text}})
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)
    pprint(status.json())
    return


def send_url(fbid, text, url, **kwargs):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s' % PAGE_ACCESS_TOKEN
    response_msg = json.dumps({
        'recipient': {
            "id": fbid
        }, 'message': {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": text,
                    "buttons": [
                        {
                            "type": "web_url",
                            "url": url,
                            "title": "click here",
                            "webview_height_ratio": "full"
                        }
                    ]
                }
            }
        }
    })
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)
    pprint(status.json())
    return


def quick_reply(fbid, text, options, **kwargs):
    quick_replies = []
    for option in options:
        quick_replies.append({
            "content_type": "text",
            "title": option,
            "payload": "<POSTBACK_PAYLOAD>",
        })
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s' % PAGE_ACCESS_TOKEN
    response_msg = json.dumps({
        'recipient': {
            "id": fbid
        }, 'message': {
            "text": text,
            "quick_replies": quick_replies
        }
    })
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)
    pprint(status.json())
    return


reply_types = {"send_message": send_message, "send_url": send_url, "quick_reply": quick_reply}


def process_message(fbid, message: str):
    pprint(fbid)
    requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + PAGE_ACCESS_TOKEN,
                  headers={"Content-Type": "application/json"},
                  data=json.dumps({
                      "recipient": {
                          "id": fbid
                      },
                      "sender_action": "typing_on"
                  }))

    user = get_user(fbid)
    arguments = {'user': user, 'fbid': fbid}

    result = get_response(user, message)
    pprint(result)
    intent = result['source']
    if 'fulfillment' not in result or result['score'] <= 0.5:
        intent = 'None'
        result['score'] = 1
    if intent in intents and result['score'] > 0.5:
        arguments.update(result['parameters'])
        intent_reply = intents.get(intent, none_reply)
        message_dict = intent_reply(**arguments)
        reply_type = reply_types[message_dict.pop('type', 'send_message')]
        reply_type(fbid, **message_dict)
    else:
        send_message(fbid, text=result['fulfillment']['speech'])
