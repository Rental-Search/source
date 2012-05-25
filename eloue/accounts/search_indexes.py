#-*- coding: utf-8 -*-
import datetime

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from haystack.sites import site
from haystack.indexes import CharField, DateTimeField, DateField, FloatField, MultiValueField, EdgeNgramField, IntegerField, DecimalField, BooleanField
from haystack.exceptions import AlreadyRegistered
from haystack.query import SearchQuerySet

from queued_search.indexes import QueuedSearchIndex

from eloue.accounts.models import Patron

class PatronIndex(QueuedSearchIndex):
    username = CharField(model_attr='username')
    avatar = CharField()
    lat = FloatField(null=True)
    lng = FloatField(null=True)
    sites = MultiValueField(faceted=True)
    date_joined_date = DateField()
    text = CharField(document=True)

    def prepare_sites(self, obj):
        return [site.id for site in obj.sites.all()]
    
    def prepare_date_joined_date(self, obj):
        return obj.date_joined.date()

    def prepare_avatar(self, obj):
        try:
            return obj.avatar.thumbnail.url
        except ObjectDoesNotExist as e:
            return settings.MEDIA_URL + "images/default_avatar.png"

    def prepare_lat(self, obj):
        return obj.default_address.position[0] if obj.default_address and obj.default_address.position else None
        try:
            return obj.default_address.position[0]
        except ObjectDoesNotExist as e:
            return None

    def prepare_lng(self, obj):
        return obj.default_address.position[1] if obj.default_address and obj.default_address.position else None
        try:
            return obj.default_address.position[1]
        except ObjectDoesNotExist as e:
            return None

    def index_queryset(self):
        return Patron.on_site.all()

try:
    site.register(Patron, PatronIndex)
except AlreadyRegistered:
    pass

patron_search = SearchQuerySet().models(Patron).facet('sites').narrow('sites:%s' % settings.SITE_ID)