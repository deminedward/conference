# -*- coding: utf-8 -*-
import json
import datetime

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import *


def event_page(request, event_pk):
    event = Event.objects.get(pk=event_pk)
    data = {}
    data['event'] = event.to_json()

    data['schedule_list'] = {}
    for s in Schedule.objects.filter(event=event):
        data['schedule_list'][s.pk] = s.to_json()
        data['schedule_list'][s.pk]['questions'] = {}
        for q in Question.objects.filter(schedule=s):
            data['schedule_list'][s.pk]['questions'][q.pk] = q.to_json()

    data['speaker_list'] = {}
    for s in MyUser.objects.filter(event=event, is_speaker=True):
        data['speaker_list'][s.pk] = s.to_json()

    data_wrapped = {'data': data}
    return JsonResponse(data_wrapped, safe=False)


def schedule_list(request, event_pk):
    data = {}
    event = Event.objects.get(pk=event_pk)
    for s in Schedule.objects.filter(event_id=event.pk):
        data[s.pk] = s.to_json()

    data_wrapped = {'data': data}
    return JsonResponse(data_wrapped, safe=False)


def index(request):
    events = Event.objects.all()
    context = {}
    context['events'] = events
    return render(request, 'index.html', context)


def user_info(request, user_pk):
    data = {}
    user = MyUser.objects.get(pk=user_pk)
    data[user.pk] = user.to_json()

    data_wrapped = {'data': data}
    return JsonResponse(data_wrapped, safe=False)