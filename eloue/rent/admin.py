# -*- coding: utf-8 -*-
from django.contrib import admin

from eloue.rent.models import Booking


class BookingAdmin(admin.ModelAdmin):
    list_filter = ('started_at', 'ended_at', 'state', 'created_at')
    raw_id_fields = ('owner', 'borrower', 'product')
    list_display = ('uuid', 'started_at', 'ended_at', 'created_at', 'total_amount', 'state')


admin.site.register(Booking, BookingAdmin)
