# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from eloue.rent.models import Booking


class BookingAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('state', 'product', 'started_at', 'ended_at')}),
        (_('Borrower & Owner'), {'fields': ('borrower', 'owner', 'ip')}),
        (_('Payment'), {'fields': ('total_amount', 'insurance_amount', 'deposit_amount', 'currency')}),
    )
    list_filter = ('started_at', 'ended_at', 'state', 'created_at')
    raw_id_fields = ('owner', 'borrower', 'product')
    list_display = ('uuid', 'started_at', 'ended_at', 'created_at', 'total_amount', 'state')


admin.site.register(Booking, BookingAdmin)
