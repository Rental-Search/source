# -*- coding: utf-8 -*-
import logbook

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site

from accounts.models import Patron
from datetime import timedelta
import datetime

from rent.models import Booking, OwnerComment, BorrowerComment, Sinister, BookingLog
from rent.choices import BOOKING_STATE

from eloue.admin import CurrentSiteAdmin

log = logbook.Logger('eloue')

class BookingLogInline(admin.TabularInline):
    model = BookingLog
    readonly_fields = ('source_state', 'target_state', 'created_at')
    extra = 0


class FraudeFilter(admin.SimpleListFilter):
    title = _('fraudes')
    parameter_name = 'total_amount'
    d1 = datetime.datetime.now() - timedelta(days=1)

    def lookups(self, request, model_admin):
        return (
            ('100+', _('plus de 100e')),
            ('outlook_bor', _('proprietaire email outlook')),
            ('outlook_own', _('locataire email outlook')),
            ('created-started', _('demande et debut de location le meme jour')),
        )
    def queryset(self, request, queryset):
        if self.value() == '100+':
            return queryset.filter(total_amount__gte=100.00)
        if self.value() == 'outlook_bor':
            return queryset.filter(borrower__email__icontains='outlook')
        if self.value() == 'outlook_own':
            return queryset.filter(owner__email__icontains='outlook')
        if self.value() == 'created-started':
            return queryset.filter(started_at=self.d1, created_at=self.d1)
        #il reste a faire les reservations pour un produit sans messages echanges.
        #et enfin à combiner les filtre

#pas certain que ca marche vraiment... meme avec 300days de timedelta cela ne s'affiche pas
class Mechants(FraudeFilter):
    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        if qs.filter(borrower__date_joined__day=self.d1.day, borrower__date_joined__month=self.d1.month, borrower__date_joined__year=self.d1.year).filter(owner__date_joined__day=self.d1.day, owner__date_joined__month=self.d1.month, owner__date_joined__year=self.d1.year):
            yield ('subscribe_date', _('date inscriptions louche'))
        if qs.filter(started_at=self.d1, created_at=self.d1):
            yield ('subscribe_date', _('date inscriptions louche'))


class BookingAdmin(CurrentSiteAdmin):
    date_hierarchy = 'created_at'
    readonly_fields = ('borrower_profil_link', 'owner_profil_link', 'transaction_line')
    fieldsets = (
        (None, {'fields': ('state', 'product', 'started_at', 'ended_at')}),
        (_('Transaction'), {'fields': ('transaction_line',)}),
        (_('Borrower & Owner'), {'fields': (('borrower', 'borrower_profil_link'), ('owner', 'owner_profil_link'), 'ip')}),
        (_('Payment'), {'fields': ('total_amount', 'insurance_amount', 'deposit_amount', 'currency')}),
    )
    list_filter = ('started_at', 'ended_at', 'state', 'created_at', FraudeFilter, Mechants)
    raw_id_fields = ('owner', 'borrower', 'product')
    list_display = ('product_name', 'borrower_url', 'borrower_phone', 'borrower_email', 'owner_url', 'owner_phone', 'owner_email',
        'started_at', 'ended_at', 'created_at', 'total_amount', 'state')
    ordering = ['-created_at']
    actions = ['send_recovery_email']
    search_fields = ['product__summary', 'owner__username', 'owner__email', 'borrower__email', 'borrower__username', 'ip']

    def owner_profil_link(self, obj):
        owner = obj.owner
        owner_profil_link = '<a href="/edit/accounts/patron/%s" target="_blank">Lien vers la page du proprietaire</a>' % owner.pk
        return _(owner_profil_link) 
    owner_profil_link.allow_tags = True
    owner_profil_link.short_description = _(u"Profil Owner")

    def borrower_profil_link(self, obj):
        borrower = obj.borrower
        borrower_profil_link = '<a href="/edit/accounts/patron/%s" target="_blank">Lien vers la page du locataire</a>' % borrower.pk
        return _(borrower_profil_link) 
    borrower_profil_link.allow_tags = True
    borrower_profil_link.short_description = _(u"Profil locataire")


    def queryset(self, request):
        current_site = Site.objects.get_current()
        if current_site.pk == 1:
            return super(BookingAdmin, self).queryset(request)
        else:
            return super(BookingAdmin, self).queryset(request).filter(source=current_site)
    
    def send_recovery_email(self, request, queryset):
        for booking in queryset:
            if booking.state == BOOKING_STATE.AUTHORIZING:
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

    def transaction_line(self, obj):
        product_type = None
        try:
            obj.product.carproduct
            product_type = "voiture"
        except:
            pass
        try:
            obj.product.realestateproduct
            product_type = "logement"
        except:
            pass
        
        if not product_type:
            product_type = "objet"

        infos = ["%s" % obj.uuid, "%s" % obj.product.summary.replace("\n", " ").replace("\r", " ").replace("|", " "), "%s" % obj.state, product_type, "%s" % obj.total_amount, "%s" % obj.started_at.strftime("%d/%m/%y"), "%s" % obj.ended_at.strftime("%d/%m/%y"), "%s" % obj.created_at.strftime("%d/%m/%y")]

        return "|".join(infos)

class CommentAdmin(admin.ModelAdmin):
    raw_id_fields = ('booking',)
    fieldsets = (
        (None, {
            'fields': ('comment', 'note', 'booking', 'created_at')
        }),
    )
    list_display = ('comment', 'note', 'booking', 'created_at')
    readonly_fields = ('created_at',)

class SinisterAdmin(admin.ModelAdmin):
    def booking(obj):
        return obj.booking_id
    list_display = ('uuid', booking, 'patron', 'product', 'created_at')
    fields = ('patron', 'product', 'description', booking, 'created_at')
    readonly_fields = (booking, 'product', 'patron', 'created_at')
    
try:
    admin.site.register(Booking, BookingAdmin)
    admin.site.register(OwnerComment, CommentAdmin)
    admin.site.register(BorrowerComment, CommentAdmin)
    admin.site.register(Sinister, SinisterAdmin)
except admin.sites.AlreadyRegistered, e:
    log.warn('Site is already registered : %s' % e)




















