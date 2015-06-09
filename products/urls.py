# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns, url
from django.utils.translation import ugettext as _

from .search import product_search
from .views import (
    ProductListView, ProductDetailView, PublishItemView,
    SuggestCategoryView, CategoryDetailView, LandingPagePublishItemView
)

urlpatterns = patterns('',
    url(r'^categorie/(?P<slug>[-\w]+)/$', CategoryDetailView.as_view(), name='category_homepage'),
    url(r'^%s/(?P<campagn_name>\w+)/$' % _('deposer'), LandingPagePublishItemView.as_view(), name='landing_page_publish_item'),
    url(r'^%s/category/$' % _('ajouter'), SuggestCategoryView.as_view(), name='suggest_category'),
    url(r'^%s/$' % _('ajouter'), PublishItemView.as_view(), name='publish_item'),
    url(r'^([^/].+/)(?P<slug>[-\w]+)-(?P<pk>\d+)/$', ProductDetailView.as_view(), {'sqs': product_search}, name='booking_create'),
    url(r'^([^/].+/)?$', ProductListView.as_view(), {'sqs': product_search.filter(is_allowed=True)}, name='product_list'),
)
