# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns, url
from django.utils.translation import ugettext as _

from .search import product_search
from .views import (
    ProductListView, ProductDetailView, PublishItemView, SuggestCategoryView, CategoryDetailView
)


product_extra_context = {'sqs': product_search}

urlpatterns = patterns('',
    url(r'^%s/$' % _('deposer'), PublishItemView.as_view(), name='publish_item2'),
    url(r'^%s/category/$' % _('ajouter'), SuggestCategoryView.as_view(), name='suggest_category'),
    url(r'^%s/$' % _('ajouter'), PublishItemView.as_view(), name='publish_item'),
    url(r'^([^/].+/)(?P<slug>[-\w]+)-(?P<pk>\d+)/$', ProductDetailView.as_view(), product_extra_context, name='booking_create'),
    url(r'^([^/].+/)?$', ProductListView.as_view(), product_extra_context, name='product_list'),
    url(r'^category/(?P<slug>[-\w]+)/$', CategoryDetailView.as_view(),
        name='category_detail'),
)
