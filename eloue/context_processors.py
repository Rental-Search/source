# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.sites.models import Site

from eloue.products.models import MessageThread

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
        # return {
        #     'unread_message_count': ProductRelatedMessage.objects.filter(
        #         recipient=request.user, 
        #         read_at=None
        #     )
        # }
	    return {
            'unread_message_count': len(filter(lambda thread: thread.new_sender(), MessageThread.objects.filter(sender=request.user))) +
	      len(filter(lambda thread: thread.new_recipient(), MessageThread.objects.filter(recipient=request.user)))
	    }
    else:
        return {}