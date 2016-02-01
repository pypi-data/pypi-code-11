# -*- coding: utf-8 -*-

from django.conf.urls import *

from .views import get_tags_recommendation

urlpatterns = [
    url('^$', get_tags_recommendation, name='tags_recommendation'),
]
