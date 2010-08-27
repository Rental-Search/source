# -*- coding: utf-8 -*-
from django.conf import settings
from django.views.decorators.cache import never_cache, cache_page
from django.views.generic.simple import direct_to_template, redirect_to
from django.views.generic.list_detail import object_detail

from eloue.products.models import Product

def product_detail(request, slug, product_id):
    return object_detail(request, queryset=Product.objects.active(), object_id=product_id)
