from pprint import pprint

from threading import Thread
import json
from django.http import HttpRequest
from django.http import HttpResponse
from django.utils.decorators import method_decorator
# Create your views here.
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework import serializers
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from bot import messenger
from .models import CheckinStore, UserActivity


class FacebookRequest(View):

    def get(self, request: HttpRequest, *args, **kwargs):
        if 'hub.verify_token' in self.request.GET and self.request.GET['hub.verify_token'] == "sanvi the chat bot":
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return View.dispatch(self, request, *args, **kwargs)

    #receives messages from facebook user
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


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivity
        fields = ('id','activity_name','is_productive')


class CheckinStoreSerializer(serializers.ModelSerializer):
    activity = ActivitySerializer()
    class Meta:
        model = CheckinStore
        fields = ('id','check_in_time','check_out_time','total_time','activity')
    pass


class UserStats(ListAPIView):
    serializer_class = CheckinStoreSerializer
    model = CheckinStore
    def get_queryset(self):
        id = self.kwargs['pk']
        qs = CheckinStore.objects.filter(activity__uid__id=id)
        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        id = kwargs['pk']
        d = {}
        data = ActivitySerializer(UserActivity.objects.filter(uid__id=id),many=True).data
        for i in data:
            id = i['id']
            d[id] = dict(i)
            d[id]['list'] = []

        for i in serializer.data:
            id = i['activity']['id']
            t = dict(i)
            t.pop('activity')
            d[id]['list'].append(t)
        return Response(d.values())
    pass
