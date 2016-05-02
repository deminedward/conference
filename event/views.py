# -*- coding: utf-8 -*-
import json
import datetime
import os

from django.shortcuts import render, get_object_or_404
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


@csrf_exempt
def vote(request, question_pk):
    question = get_object_or_404(Question, pk=question_pk)
    if request.method == 'POST':
        print(eval(request.body)['choice_pk'])
        choice = Choice.objects.get(pk=eval(request.body)['choice_pk'])
        if choice.question == question:
            choice.vote_counter += 1
            choice.save()

    data_wrapped = {'data': {}}
    return JsonResponse(data_wrapped, safe=False)


def vote_results(request, question_pk):
    question = Question.objects.get(pk=question_pk)
    data = {}
    data[question_pk] = question.question_text
    data['votest'] = {}
    choices = Choice.objects.filter(question=question)
    for c in choices:
        data['votest'][c.pk] = {'text': c.choice_text, 'votes': c.vote_counter}

    data_wrapped = {'data': data}
    return JsonResponse(data_wrapped, safe=False)