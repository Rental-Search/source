# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib import admin
from django.contrib.flatpages.models import FlatPage
from django.contrib.flatpages.admin import FlatPageAdmin



class CurrentSiteAdmin(admin.ModelAdmin):
    def queryset(self, request):
        if request.user.is_superuser:
            queryset = self.model.objects.get_query_set().filter(**{'sites__id__exact': settings.SITE_ID})
            ordering = self.ordering or ()  # otherwise we might try to *None, which is bad ;)
            if ordering:
                queryset = queryset.order_by(*ordering)
            return queryset
        else:
            return super(CurrentSiteAdmin, self).queryset(request)
    

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
    

admin.site.unregister(FlatPage)
admin.site.register(FlatPage, CustomFlatPageAdmin)
