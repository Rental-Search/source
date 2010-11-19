# -*- coding: utf-8 -*-
from django.core.cache import cache

from eloue.utils import cache_key


def post_save_answer(sender, instance, created, **kwargs):
    instance.question.save()


def post_save_product(sender, instance, created, **kwargs):
    cache.delete(cache_key('product:row', instance.id, None, None))
    cache.delete(cache_key('product:patron:row', instance.id))
