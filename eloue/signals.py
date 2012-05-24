# -*- coding: utf-8 -*-
from django.conf import settings
import re
from eloue.payments.paybox_payment import PayboxManager

REPLACE_STRING = settings.REPLACE_STRING

def post_save_sites(sender, instance, created, **kwargs):
    instance.sites.add(*settings.DEFAULT_SITES)

def pre_delete_creditcard(sender, instance, *args, **kwargs):
    PayboxManager().unsubscribe(instance.holder.pk)

def _string_filter(raw_string):
    
    sub_string = re.sub(r"\+\d{11}", REPLACE_STRING, raw_string, re.I) #phone number filter, for +33698756789
    sub_string = re.sub(r"(\w+(.)\w+@\w+(?:\.\w+)+)", REPLACE_STRING, sub_string, re.I) #e-mail filter lin.liu@gmail.com
    sub_string = re.sub(r"(\w+(.)\w+@\w+\-\w+(?:\.\w+)+)", REPLACE_STRING, sub_string, re.I) #e-mail filter lin.liu@e-loue.com
    sub_string = re.sub(r"\d{10}", REPLACE_STRING, sub_string, re.I)  #phone number filter, for 0690987891
    sub_string = re.sub(r"\d{2} \d{2} \d{2} \d{2} \d{2}", REPLACE_STRING, sub_string, re.I) #phone number filter, for 06 87 65 53 89
    return sub_string

def message_content_filter(sender, instance, signal, *args, **kwargs):
    """
    The informations that e-loue want to hide are: 
    phone number,
    e-mail address.
    """
    subject = instance.subject
    body = instance.body
    instance.subject = _string_filter(subject)
    instance.body = _string_filter(body)


def message_site_filter(sender, instance, signal, *args, **kwargs):
    """
    Filter to forbiden passing message between users from different sites.
    """
    from eloue.accounts.models import Patron
    if instance.sender and instance.recipient:
        patron_sender = Patron.objects.get(pk=instance.sender.pk)
        patron_recipient = Patron.objects.get(pk=instance.recipient.pk)
        sender_sites = patron_sender.sites.all()
        recipient_sites = patron_recipient.sites.all()
        if set(sender_sites) & set(recipient_sites):
            pass
        else:
            instance.recipient = None
    
    
    