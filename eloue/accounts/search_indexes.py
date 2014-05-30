#-*- coding: utf-8 -*-
from haystack import indexes

from accounts.models import Patron

__all__ = ['PatronIndex']


class PatronIndex(indexes.Indexable, indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=False)
    location = indexes.LocationField(model_attr='default_address__position', null=True)

    username = indexes.CharField(model_attr='username')
    avatar = indexes.CharField(null=True)
    sites = indexes.MultiValueField(faceted=True)
    date_joined_date = indexes.DateField(model_attr='date_joined__date')
    url = indexes.CharField(model_attr='get_absolute_url')

    def prepare_sites(self, obj):
        res = obj.sites.all().values_list('id', flat=True)
        return tuple(res)

    def prepare_avatar(self, obj):
        if obj.avatar:
            return obj.thumbnail.url

    def get_model(self):
        return Patron

    def index_queryset(self, using=None):
        return self.get_model().on_site.all()
