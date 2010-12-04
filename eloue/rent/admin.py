# -*- coding: utf-8 -*-
from django.contrib import admin

from eloue.rent.models import Booking


class BookingAdmin(admin.ModelAdmin):
    list_filter = ('started_at', 'ended_at', 'state')
    raw_id_fields = ('owner', 'borrower')
    list_display = ('product__summary', 'started_at', 'ended_at', 'created_at', 'total_amount')


admin.site.register(Booking, BookingAdmin)
