
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from pprint import pprint

from django.shortcuts import render

# Create your views here.
from django.views import View
from django.http import HttpResponse
from django.http import HttpRequest
from bot import messenger
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from threading import Thread


class FacebookRequest(View):

    def get(self, request: HttpRequest, *args, **kwargs):
        if 'hub.verify_token' in self.request.GET and self.request.GET['hub.verify_token'] == "sanvi the chat bot":
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return View.dispatch(self, request, *args, **kwargs)

    def post(self, request: HttpRequest, *args, **kwargs):
        params = request.POST
        print(params)
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        pprint(incoming_message)
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                if 'message' in message and 'text' in message['message']:
                    arguments = (message['sender']['id'], message['message']['text'])
                    t = Thread(target=messenger.process_message, args=arguments)
                    t.start()
        return HttpResponse()


@login_required
def home(request):
    return render(request, 'core/home.html')
