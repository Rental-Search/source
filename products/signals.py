# -*- coding: utf-8 -*-
from django.core.cache import cache
from django.contrib.sites.models import Site

from eloue.utils import cache_key
from django.db.models import signals
from django.core import exceptions

def post_save_answer(sender, instance, created, **kwargs):
    instance.question.save()


def post_save_product(sender, instance, created, **kwargs):
    cache.delete(cache_key('product:patron:row', instance.id))
    
    cache.delete(cache_key('product:meta', instance.pk))
    cache.delete(cache_key('product:breadcrumb', instance.pk))
    cache.delete(cache_key('product:details:before_csrf', instance.pk, Site.objects.get_current().pk))
    cache.delete(cache_key('product:details:after_csrf', instance.pk, Site.objects.get_current().pk))
    cache.delete(cache_key('product:details:after_dates', instance.pk))


def post_save_to_update_product(sender, instance, created, **kwargs):
    try:
        product = instance.product
        if product is not None:
            # Fixed issues with picture.json fixture when running tests:
            # it doesn't make sense to emit signal for None product
            signals.post_save.send(
                sender=product.__class__, instance=product,
                raw=False, created=False
            )
    except exceptions.ObjectDoesNotExist:
        pass

def post_save_to_batch_update_product(sender, instance, created, **kwargs):
    for product in instance.products.all():
        signals.post_save.send(
            sender=product.__class__, instance=product,
            raw=False, created=False
        )


def post_save_curiosity(sender, instance, created, **kwargs):
    cache.delete(cache_key('curiosities', Site.objects.get_current()))


def post_save_message(sender, instance, created, **kwargs):
    if not created:
        return

    # perform thread updates after creating a new message
    thread = instance.thread
    if thread:
        # update archive states
        if instance.sender == thread.sender:
            if thread.recipient_archived:
                thread.recipient_archived = False
        elif instance.sender == thread.recipient:
            if thread.sender_archived:
                thread.sender_archived = False
        # TODO: should we log or notify user somehow if message's sender is not a participant of the message thread?

        # update message thread to point to the created message
        thread.last_message = instance
        # FIXME: should we rally update 'last_offer'? I didn't find any use of it
        if instance.offer:
            thread.last_offer = instance

        thread.save()

    # perform parent message updates after creating a new message
    parent_msg = instance.parent_msg
    if parent_msg:
        parent_msg.replied_at = instance.sent_at
        parent_msg.save()
