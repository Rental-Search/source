# -*- coding: utf-8 -*-
from django.core.cache import cache
from django.contrib.sites.models import Site
import datetime
from eloue.utils import cache_key


def post_save_answer(sender, instance, created, **kwargs):
    instance.question.save()


def post_save_product(sender, instance, created, **kwargs):
    cache.delete(cache_key('product:row', instance.id, None, None))
    cache.delete(cache_key('product:patron:row', instance.id))


def post_save_curiosity(sender, instance, created, **kwargs):
    cache.delete(cache_key('curiosities', Site.objects.get_current()))
