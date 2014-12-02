# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.cache import cache
from django.contrib.sites.models import Site
from django.db.models import get_model
from django.db.models.query_utils import Q

from eloue.utils import cache_key, create_alternative_email
from django.db.models import signals
from django.core import exceptions


def post_save_answer(sender, instance, created, **kwargs):
    instance.question.save()


ELOUE_SITE_ID = 1
GOSPORT_SITE_ID = 13


def post_save_product(sender, instance, created, **kwargs):
    cache.delete(cache_key('product:patron:row', instance.id))
    
    cache.delete(cache_key('product:meta', instance.pk))
    cache.delete(cache_key('product:breadcrumb', instance.pk))
    cache.delete(cache_key('product:details:before_csrf', instance.pk, Site.objects.get_current().pk))
    cache.delete(cache_key('product:details:after_csrf', instance.pk, Site.objects.get_current().pk))
    cache.delete(cache_key('product:details:after_dates', instance.pk))

    CategoryConformity = get_model('products', 'CategoryConformity')
    Product2Category = get_model('products', 'Product2Category')

    category = instance.category
    conformity = None
    while category and not conformity:
        try:
            conformity = CategoryConformity.objects.filter(
                Q(gosport_category=category) | Q(eloue_category=category)
            )[0]
        except IndexError:
            category = category.parent

    if not conformity:
        Product2Category.objects.filter(product=instance).delete()
        Product2Category.objects.create(product=instance, category=instance.category, site_id=settings.SITE_ID)
    else:
        Product2Category.objects.filter(product=instance).delete()
        Product2Category.objects.create(product=instance, category=conformity.gosport_category, site_id=GOSPORT_SITE_ID)
        Product2Category.objects.create(product=instance, category=conformity.eloue_category, site_id=ELOUE_SITE_ID)


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


def new_message_email(sender, instance, created, **kwargs):
    """
    This function sends an email and is called via Django's signal framework.
    Optional arguments:
        ``template_name``: the template to use
        ``subject_prefix``: prefix for the email subject.
        ``default_protocol``: default protocol in site URL passed to template
    """
    if created and instance.recipient.email:
        context = {'message': instance}
        message = create_alternative_email(
            'django_messages/new_message', context, settings.DEFAULT_FROM_EMAIL, [instance.recipient.email])
        message.send()
