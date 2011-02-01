# -*- coding: utf-8 -*-
from django.contrib import admin


class CurrentSiteAdmin(admin.ModelAdmin):
    def queryset(self, request):
        if request.user.is_superuser:
            queryset = self.model.objects.get_query_set()
            ordering = self.ordering or () # otherwise we might try to *None, which is bad ;)
            if ordering:
                queryset = queryset.order_by(*ordering)
            return queryset
        else:
            return super(CurrentSiteAdmin, self).queryset(request)
    
