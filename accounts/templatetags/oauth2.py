# -*- coding: utf-8 -*-
from django import template

from rest_framework.views import APIView

register = template.Library()

@register.filter
def oauth2_user(value):
    return APIView().initialize_request(value).user
