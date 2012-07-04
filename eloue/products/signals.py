# -*- coding: utf-8 -*-
from django.core.cache import cache
from django.contrib.sites.models import Site
import datetime
from eloue.utils import cache_key
from django.db.models import signals
from django.core import exceptions

def post_save_answer(sender, instance, created, **kwargs):
    instance.question.save()


def post_save_product(sender, instance, created, **kwargs):
    cache.delete(cache_key('product:patron:row', instance.id))
    
    cache.delete(cache_key('product:meta', instance.pk))
    cache.delete(cache_key('product:breadcrumb', instance.pk))
    cache.delete(cache_key('product:details:before_csrf', instance.pk))
    cache.delete(cache_key('product:details:after_csrf', instance.pk, Site.objects.get_current().pk))
    cache.delete(cache_key('product:details:after_dates', instance.pk))


def post_save_to_update_product(sender, instance, created, **kwargs):
	try:
		product = instance.product
		signals.post_save.send(
			sender=product.__class__, instance=product, 
			raw=False, created=False
		)
	except exceptions.ObjectDoesNotExist:
		pass

def post_save_to_batch_update_product(sender, instance, created, **kwargs):
	for product in instance.products.all():
		signals.post_save.send(sender=product.__class__, instance=product, raw=False, created=False)


def post_save_curiosity(sender, instance, created, **kwargs):
    cache.delete(cache_key('curiosities', Site.objects.get_current()))
