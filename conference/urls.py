# -*- coding: utf-8 -*-
"""conference URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from event import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/event/(?P<event_pk>[0-9]+)/$', views.event_page, name='event_page'),
    url(r'^api/schedule/(?P<event_pk>[0-9]+)/$', views.schedule_list, name='schedule_list'),
    url(r'^api/index/$', views.index, name='index'),
    url(r'^api/user_info/(?P<user_pk>[0-9]+)/$', views.user_info, name='user_info'),
    url(r'^api/vote_results/(?P<question_pk>[0-9]+)/$', views.vote_results, name='vote_results'),
    url(r'^api/vote/(?P<question_pk>[0-9]+)/$', views.vote, name='vote'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
