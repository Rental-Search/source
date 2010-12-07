# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from eloue.rent.models import Booking


class BookingAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    fieldsets = (
        (None, {'fields': ('state', 'product', 'started_at', 'ended_at')}),
        (_('Borrower & Owner'), {'fields': ('borrower', 'owner', 'ip')}),
        (_('Payment'), {'fields': ('total_amount', 'insurance_amount', 'deposit_amount', 'currency')}),
    )
    list_filter = ('started_at', 'ended_at', 'state', 'created_at')
    raw_id_fields = ('owner', 'borrower', 'product')
    list_display = ('uuid', 'started_at', 'ended_at', 'created_at', 'total_amount', 'state')
    ordering = ['-created_at']
    search_fields = ['product__summary', 'owner__username', 'owner__email', 'borrower__email', 'borrower__username']

admin.site.register(Booking, BookingAdmin)
