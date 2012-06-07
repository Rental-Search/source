# -*- coding: utf-8 -*-
import logbook

from django.conf import settings
from django.contrib import admin
from django.contrib.flatpages.models import FlatPage
from django.contrib.flatpages.admin import FlatPageAdmin


log = logbook.Logger('eloue')

class CurrentSiteAdmin(admin.ModelAdmin):
    def queryset(self, request):
        if request.user.is_superuser:
            return super(CurrentSiteAdmin, self).queryset(request)
        else:
            queryset = self.model.objects.get_query_set().filter(**{'sites__id__exact': settings.SITE_ID})
            ordering = self.ordering or ()  # otherwise we might try to *None, which is bad ;)
            if ordering:
                queryset = queryset.order_by(*ordering)
            return queryset
    

class CustomFlatPageAdmin(FlatPageAdmin):
    def queryset(self, request):
        if request.user.is_superuser:
            queryset = self.model.objects.get_query_set()
            ordering = self.ordering or ()  # otherwise we might try to *None, which is bad ;)
            if ordering:
                queryset = queryset.order_by(*ordering)
            return queryset
        else:
            return super(FlatPageAdmin, self).queryset(request).filter(**{'sites__id__exact': settings.SITE_ID})
    

try:
    admin.site.unregister(FlatPage)
    admin.site.register(FlatPage, CustomFlatPageAdmin)
except admin.sites.AlreadyRegistered, e:
    log.warn('Site is already registered : %s' % e)
