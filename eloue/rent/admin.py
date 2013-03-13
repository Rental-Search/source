# -*- coding: utf-8 -*-
import logbook

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from eloue.admin import CurrentSiteAdmin
from eloue.rent.models import Booking, OwnerComment, BorrowerComment, Sinister, BookingLog

log = logbook.Logger('eloue')

class BookingLogInline(admin.TabularInline):
    model = BookingLog
    readonly_fields = ('source_state', 'target_state', 'created_at')
    extra = 0

class BookingAdmin(CurrentSiteAdmin):
    date_hierarchy = 'created_at'
    fieldsets = (
        (None, {'fields': ('state', 'product', 'started_at', 'ended_at')}),
        (_('Borrower & Owner'), {'fields': ('borrower', 'owner', 'ip')}),
        (_('Payment'), {'fields': ('total_amount', 'insurance_amount', 'deposit_amount', 'currency')}),
    )
    list_filter = ('started_at', 'ended_at', 'state', 'created_at')
    raw_id_fields = ('owner', 'borrower', 'product')
    list_display = ('product_name', 'borrower_url', 'borrower_phone', 'borrower_email', 'owner_url', 'owner_phone', 'owner_email',
        'started_at', 'ended_at', 'created_at', 'total_amount', 'state')
    ordering = ['-created_at']
    actions = ['send_recovery_email']
    search_fields = ['product__summary', 'owner__username', 'owner__email', 'borrower__email', 'borrower__username']
    
    def send_recovery_email(self, request, queryset):
        for booking in queryset:
            if booking.state == Booking.STATE.AUTHORIZING:
                booking.send_recovery_email()
    send_recovery_email.short_description = _(u"Envoyer un email de relance")
    
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
    
    def borrower_email(self, obj):
        return '<a href="mailto:%(email)s">%(email)s</a>' % {'email': obj.borrower.email}
    borrower_email.short_description = _('Borrower email')
    borrower_email.allow_tags = True
    
    def borrower_phone(self, obj):
        if obj.borrower.phones.exists():
            return obj.borrower.phones.all()[0]
    borrower_phone.short_description = _('Borrower phone')
    
    def owner_url(self, obj):
        return '<a href="%s">%s</a>' % (
            reverse('admin:accounts_patron_change', args=[obj.owner.pk]),
            obj.owner.username
        )
    owner_url.short_description = _('Owner')
    owner_url.allow_tags = True
    
    def owner_email(self, obj):
        return '<a href="mailto:%(email)s">%(email)s</a>' % {'email': obj.owner.email}
    owner_email.short_description = _('Owner email')
    owner_email.allow_tags = True
    
    def owner_phone(self, obj):
        if obj.owner.phones.exists():
            return obj.owner.phones.all()[0]
    owner_phone.short_description = _('Owner phone')
    inlines = [BookingLogInline, ]

class CommentAdmin(admin.ModelAdmin):
    raw_id_fields = ('booking',)
    fieldsets = (
        (None, {
            'fields': ('comment', 'note', 'booking')
        }),
    )
    list_display = ('comment', 'note', 'booking')

class SinisterAdmin(admin.ModelAdmin):
    def booking(obj):
        return obj.booking_id
    list_display = ('uuid', booking, 'patron', 'product',)
    fields = ('patron', 'product', 'description', booking)
    readonly_fields = (booking, 'product', 'patron')
    
try:
    admin.site.register(Booking, BookingAdmin)
    admin.site.register(OwnerComment, CommentAdmin)
    admin.site.register(BorrowerComment, CommentAdmin)
    admin.site.register(Sinister, SinisterAdmin)
except admin.sites.AlreadyRegistered, e:
    log.warn('Site is already registered : %s' % e)
