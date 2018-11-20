import json, requests, random, re
from pprint import pprint
from bot import nlpluisai
import wikipedia
from word2number.w2n import word_to_num

PAGE_ACCESS_TOKEN = "EAACwSutJ0Q8BAC42dpG0pfwrThBVFKzehsxLGNd7RsewBdA5TheMOZCfW6HtXQxrxaGPa8zdLHtZAvuWdLz7mvTRx926vf1ZB0uXcp2iz2O12NHVRdNlb1GsZANDJ2uBW88BqMVtCQxBwN4lY67jdPFh1Ce1PSdE4EhZAU9zE7mTOznA3psN5"


def send_message(fbid, message):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s' % PAGE_ACCESS_TOKEN
    response_msg = json.dumps({"recipient": {"id": fbid}, "message": {"text": message}})
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)
    pprint(status.json())
    return


def greeting_reply(**kwargs) -> str:
    reply: str = random.choice(['hi', 'hello', 'hey', 'namaste'])
    if 'fbid' in kwargs:
        fbid = kwargs['fbid']
        user_details_url = "https://graph.facebook.com/v2.6/%s" % fbid
        user_details_params = {'fields': 'first_name', 'access_token': PAGE_ACCESS_TOKEN}
        user_details = requests.get(user_details_url, user_details_params).json()
        if 'first_name' in user_details:
            reply += " " + user_details['first_name']
    return reply


def wiki_reply(**kwargs) -> str:
    reply: str = ""
    try:
        if 'searchkey' in kwargs:
            reply: str = wikipedia.summary(kwargs['searchkey'], sentences=2)
    except wikipedia.exceptions.PageError as ex:
        try:
            reply: str = wikipedia.summary(wikipedia.search(kwargs['searchkey'], results=1)[0], sentences=2)
        except Exception:
            reply = "did not find any results regarding " + kwargs['searchkey']
        pass
    except wikipedia.exceptions.DisambiguationError as dex:
        options = dex.options
        reply = "did you mean?\n" + "\n".join(random.sample(options, 5))
    return reply


def work_reply(**kwargs) -> str:
    reply: str = ""
    try:
        if 'time' in kwargs:
            time: int = word_to_num(kwargs['time'])
        else:
            time: int = 1
        if 'project' in kwargs:
            project: str = kwargs['project']
        else:
            project: str = "unproductive"
        reply += "you have worked on {project} for {time} hours".format(project=project, time=time)
        pass
    except Exception as ex:
        reply: str = ""
        pass
    return reply


def none_reply(**kwargs) -> str:
    return random.choice(['i did not get that', 'i am unable to catch your words'])


intents = {'greeting': greeting_reply, 'wiki': wiki_reply, 'work': work_reply, 'None': none_reply}


def process_message(fbid, message: str):
    # user_details_url = "https://graph.facebook.com/v2.6/%s" % fbid
    # user_details_params = {'fields': 'first_name', 'access_token': PAGE_ACCESS_TOKEN}
    # user_details = requests.get(user_details_url, user_details_params).json()
    # if 'first_name' not in user_details:
    #     return
    # message = user_details['first_name'] + " : " + message
    # send_message(fbid, message)
    pprint(fbid)
    requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + PAGE_ACCESS_TOKEN,
                  headers={"Content-Type": "application/json"}, data=json.dumps({
            "recipient": {
                "id": fbid
            },
            "sender_action": "typing_on"
        }))
    intent_dict = nlpluisai.get_intent(message)
    intent = intent_dict['topScoringIntent']['intent'] if intent_dict['topScoringIntent']['score'] > 0.5 else 'None'
    arguments = {'fbid': fbid}
    builtin = dict()
    for entity in intent_dict['entities']:
        if 'builtin' in entity['type']:
            type = entity['type'].split('.')[-1]
            builtin[type] = builtin.get(type, {})
            builtin[type][entity['entity']] = entity['resolution']['value']
            continue
        arguments[entity['type']] = entity['entity']
    message: str = intents[intent](**arguments)
    send_message(fbid, message)
    requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + PAGE_ACCESS_TOKEN,
                  headers={"Content-Type": "application/json"}, data=json.dumps({
            "recipient": {
                "id": fbid
            },
            "sender_action": "typing_off"
        }))
    pass
