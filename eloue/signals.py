# -*- coding: utf-8 -*-
from django.conf import settings
import re

def post_save_sites(sender, instance, created, **kwargs):
    instance.sites.add(*settings.DEFAULT_SITES)

def _string_filter(raw_string):
    replace_string = "### eloue suggests clients to hide their informations if the booking is not valid yet ###"
    sub_string = re.sub(r"(\w+(.)\w+@\w+(?:\.\w+)+)", replace_string, raw_string, re.I) #e-mail filter lin.liu@gmail.com
    sub_string = re.sub(r"(\w+(.)\w+@\w+\-\w+(?:\.\w+)+)", replace_string, sub_string, re.I) #e-mail filter lin.liu@e-loue.com
    sub_string = re.sub(r"\d{10}", replace_string, sub_string, re.I)  #phone number filter, for 0690987891
    sub_string = re.sub(r"\+\d{11}", replace_string, sub_string, re.I) #phone number filter, for +33698756789
    sub_string = re.sub(r"\d{2} \d{2} \d{2} \d{2} \d{2}", replace_string, sub_string, re.I) #phone number filter, for 06 87 65 53 89
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
    sender_sites = instance.sender.sites.all()
    recipient_sites = instance.recipient.sites.all()
    if set(sender_sites) & set(recipient_sites):
        print ">>>>>>>>>have right to send>>>>>>>>"
        pass
    else:
        print ">>>>>>>>>no right to send>>>>>>>>"
        instance.recipient = None