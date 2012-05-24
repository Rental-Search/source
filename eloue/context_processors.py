# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.sites.models import Site
from django.db.models import Count

from eloue.products.models import ProductRelatedMessage, MessageThread
from eloue.rent.models import Booking

def site(request):
    try:
        return {'site': Site.objects.get_current()}
    except Site.DoesNotExist:
        return {'site': None}


def debug(request):
    return {'debug': settings.DEBUG}


def facebook_context(request):
    return {'FACEBOOK_APP_ID': settings.FACEBOOK_APP_ID}


def unread_message_count_context(request):
    if request.user.is_authenticated():
        return {
            'unread_message_count': ProductRelatedMessage.objects.filter(
                recipient=request.user, read_at=None
            ).values('thread').annotate(Count('thread')).order_by().count()
        }
    else:
        return {}

