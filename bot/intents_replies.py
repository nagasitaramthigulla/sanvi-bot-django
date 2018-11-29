import json, requests, random, re
from pprint import pprint
from bot import nlpluisai
import wikipedia
from word2number.w2n import word_to_num
from bot.models import *
from datetime import datetime


def greeting_reply(user=None, **kwargs) -> dict:
    reply: str = random.choice(['Hi', 'Hello', 'Hey', 'Namaste'])
    if user is not None:
        reply += " " + user.first_name
    return {"type": "send_message", "text": reply}


def wiki_reply(**kwargs) -> dict:
    reply: str = ""
    reply_type = "send_message"
    options = []
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
        reply = "did you mean?\n" + "\n"
        options = ["wiki " + option for option in random.sample(options, 5)]
        reply_type = "quick_reply"
    return {"type": reply_type, "text": reply, "options": options}


def checkin_reply(user: MessengerUser = None, **kwargs) -> dict:
    reply: str = ""
    reply_type = "send_message"
    options = []
    try:
        if "projectname" in kwargs and user is not None:
            project_name = kwargs['projectname']
            if 'project' in project_name:
                project_name = project_name.split('-')[-1].strip().split()[-1]
            if Checkin.objects.filter(activity__uid=user.id).count() != 0:
                reply = "you have already checked into {pn} at {t}"
                checkin = Checkin.objects.get(activity__uid=user.id)
            else:# projectname is given
                if UserActivity.objects.filter(uid=user, activity_name=project_name).count() != 0:
                    reply = "checking you into {pn} at {t}"
                    user_context = json.loads(user.context)
                    activity = UserActivity.objects.get(uid=user, activity_name=project_name)
                    productivity = "prodictivity_{}".format(project_name)
                    if productivity in user_context:
                        reply += "\n you have not specified whether {pn} is productive or not?"
                        options = ["yes", "no"]
                        reply_type = "quick_reply"
                else:
                    activity = UserActivity.objects.create(uid=user, activity_name=project_name)
                    activity.save()
                    user_context = json.loads(user.context)
                    user_context["productivity_{}".format(project_name)] = False
                    user.context = json.dumps(user_context)
                    user.save()
                    reply += "\nis {pn} productive or not?"
                    options = ["yes", "no"]
                    reply_type = "quick_reply"
                checkin = Checkin.objects.create(activity=activity)
                checkin.save()
            reply = reply.format(pn=checkin.activity.activity_name,
                                 t=checkin.check_in_time.time().__str__().split('.')[0])
        else:
            reply = "you did not specify where to checkin?"
        pass
    except Exception as ex:
        reply = "unable to check you in"
        pass
    return {"type": reply_type, "text": reply, "options": options}


def productivity_reply(user: MessengerUser = None, **kwargs) -> dict:
    reply = "updated"
    try:
        if user is None:
            return none_reply()
        else:
            status = kwargs.get('productivity', "").lower() in ["yes", "productivity", "productive"]
            if "projectname" in kwargs:
                project_name = kwargs["projectname"]
            else:
                project_name = Checkin.objects.get(activity__uid=user.id).activity.activity_name
            productivity = "productivity_{}".format(project_name)
            context: dict = json.loads(user.context)
            if productivity in context:
                context.pop(productivity, False)
                user.context = json.dumps(context)
                user.save()
            activity = UserActivity.objects.get(uid=user, activity_name=project_name) if UserActivity.objects.filter(
                uid=user, activity_name=project_name).count() != 0 else None
            if activity != None:
                activity.is_productive = status
                activity.save()
            return {"type": "send_message", "text": "updated {pn} to {status}".format(pn=project_name,
                                                                                      status="productive" if status else "unproductive")}
    except Exception as ex:
        return none_reply()


def checkout_reply(user: MessengerUser = None, **kwargs) -> dict:
    reply = ""
    try:
        if user is None:
            reply = "checking you out"
        else:
            if Checkin.objects.filter(activity__uid=user.id).count() != 0:
                checkin = Checkin.objects.get(activity__uid=user)
                if "projectname" in kwargs and checkin.checked_into != kwargs["projectname"]:
                    reply = "you have not checked into {a} but into {b}".format(a=kwargs["projectname"],
                                                                                b=checkin.checked_into)
                else:
                    reply = "checking you out of {}".format(checkin.activity.activity_name)
                    checkin_store = CheckinStore.objects.create(check_in_time=checkin.check_in_time,
                                                                activity=checkin.activity)
                    checkin_store.save()
                    checkin.delete()
            else:
                reply = "you have not checked into anything"
    except Exception as ex:
        reply = "unable process your check out request"
    return {"type": "send_message", "text": reply}


def stats_reply(user: MessengerUser = None, **kwargs) -> dict:
    return {"type": "send_url", "text": "these are your stats", "url": "http://saanvidashboard.azurewebsites.net/metrics?uid={uid}".format(uid=user.id)}


def none_reply(**kwargs) -> dict:
    return {"type": "send_message", "text": random.choice(['i did not get that', 'i am unable to catch your words'])}


intents = {'greeting': greeting_reply, 'wiki': wiki_reply, 'None': none_reply, 'checkin': checkin_reply,
           'checkout': checkout_reply, 'productivity': productivity_reply, 'stats': stats_reply}
