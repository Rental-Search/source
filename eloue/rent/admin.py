# -*- coding: utf-8 -*-
from django.contrib import admin
from django.core.urlresolvers import reverse
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
    list_display = ('product_name', 'borrower_url', 'owner_url', 'started_at', 'ended_at', 'created_at', 'total_amount', 'state')
    ordering = ['-created_at']
    search_fields = ['product__summary', 'owner__username', 'owner__email', 'borrower__email', 'borrower__username']
    
    def product_name(self, obj):
        return obj.product.summary
    product_name.short_description = _('Product')
    
    def borrower_url(self, obj):
        return '<a href="%s">%s</a>' % (
            reverse('admin:accounts_patron_change', args=[obj.borrower.pk]),
            obj.borrower.username
        )
    borrower_url.short_description = _('Borrower')
    borrower_url.allow_tags = True
    
    def owner_url(self, obj):
        return '<a href="%s">%s</a>' % (
            reverse('admin:accounts_patron_change', args=[obj.owner.pk]),
            obj.owner.username
        )
    owner_url.short_description = _('Owner')
    owner_url.allow_tags = True
    

admin.site.register(Booking, BookingAdmin)
