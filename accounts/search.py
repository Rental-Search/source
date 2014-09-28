# -*- coding: utf-8 -*-
from django.conf import settings

from haystack.query import SearchQuerySet

from accounts.models import Patron

__all__ = ['patron_search']


patron_search = SearchQuerySet().models(Patron).facet('sites').narrow('sites:%s' % settings.SITE_ID)
