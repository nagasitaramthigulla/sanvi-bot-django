import requests, json, pprint
from bot.models import MessengerUser

# var = {'id': 'b405d074-f998-4f20-a5d8-f01c279c0661',
#        'lang': 'en',
#        'result': {'action': '',
#                   'actionIncomplete': False,
#                   'contexts': [],
#                   'fulfillment': {'messages': [{'speech': '', 'type': 0}],
#                                   'speech': ''},
#                   'metadata': {'intentId': 'b65604a1-04b5-4a36-bb6d-76f83438ab5e',
#                                'intentName': 'checkin',
#                                'isFallbackIntent': 'false',
#                                'webhookForSlotFillingUsed': 'false',
#                                'webhookUsed': 'false'},
#                   'parameters': {'projectname': 'facebook'},
#                   'resolvedQuery': 'i am checking into facebook',
#                   'score': 1.0,
#                   'source': 'agent'},
#        'sessionId': '1777183255667406',
#        'status': {'code': 200, 'errorType': 'success'},
#        'timestamp': '2018-12-17T15:14:18.831Z'}


def get_response(user: MessengerUser, message: str):
    context = json.loads(user.context)
    url = "https://api.dialogflow.com/v1/query"
    params = {
        "v": "20150910",
        "timezone": "Asia/Kolkata",
        "lang": "en",
        "contexts": context.get('contexts', []),
        "query": message,
        "sessionId": user.id #every user has a seperate session at dialogflow
    }
    headers = {
        "Authorization": "Bearer 003547aae8b04bbdbed8408afab99dd8",
        "Content-Type": "application/json"
    }
    result = requests.get(url=url,params=params,headers=headers)
    result_dict = result.json()

    return result_dict['result']
