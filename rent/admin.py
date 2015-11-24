# -*- coding: utf-8 -*-
import logbook

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from django.db.models import F, Count, Q

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
    parameter_name = 'critere'

    def lookups(self, request, model_admin):
        return (
            # ('100+', _('plus de 100e')),
            # ('created-started', _('demande et debut de location la meme heure')),
            # ('no-messages', _('booking sans messages enchanges')),

            # ('outlook', _('proprietaire ou locataire email outlook')),
            ('bookings_loads-without-mess', _('bcp de demandes de booking sans messages enchanges')),
            ('bookings_loads-100+', _('bcp de demandes de booking de plus de 100e')),
            ('bookings_loads', _('bcp de demandes de booking de plus de 100e ou sans messages')),
            # ('stolen-card-1', _('commence 1h apres creation')),
            # ('stolen-card-2', _('loc et prop inscris moins de 1h avant la loc')),
            
        )
    def queryset(self, request, queryset):
        # if self.value() == '100+':
        #     return queryset.filter(Q(total_amount__gte=100.00))
        # if self.value() == 'created-started':
        #     return queryset.filter(started_at__lte=F('created_at') + timedelta(hours=1))
        # if self.value() == 'no-messages':
        #     return queryset.annotate(count_messages=Count('product__messages')).filter(count_messages=0)
          
        # #OUTLOOK
        # if self.value() == 'outlook':
        #     return queryset.filter(Q(owner__email__icontains='outlook') | Q(borrower__email__icontains='outlook'))
        #     #Booking dont le locataire ou propriétaire à une adresse outlook 
        
        #VOLEUR 1
        if self.value() == 'bookings_loads-without-mess':
            return queryset.annotate(count_messages=Count('product__messages'), count_bookings=Count('borrower__bookings')).filter(Q(count_messages=0) & Q(count_bookings__gte=3) & Q(borrower__date_joined__gte=F('started_at') - timedelta(days=1)))
            #Booking sans message dont le locataire a fait plus de 3 demandes de location moins de 1 jour apres son inscription

        #VOLEUR 2
        if self.value() == 'bookings_loads-100+':
            return queryset.annotate(count_bookings=Count('borrower__bookings')).filter(Q(total_amount__gte=100.00) & Q(count_bookings__gte=3) & Q(borrower__date_joined__gte=F('started_at') - timedelta(days=1)))
            #Booking de plus de 100€ effectuée moins de 1h après l'inscription du locataire, qui lui meme a fait plus de 3 demandes de location en moins de 1j après son inscription

       #VOLEUR 3
        if self.value() == 'bookings_loads':
            return queryset.annotate(count_bookings=Count('borrower__bookings'), count_messages=Count('product__messages')).filter( Q(Q(total_amount__gte=100.00) & Q(count_bookings__gte=3) & Q(borrower__date_joined__gte=F('started_at') - timedelta(hours=3))) | Q(Q(count_messages=0) & Q(count_bookings__gte=3) & Q(borrower__date_joined__gte=F('started_at') - timedelta(days=1))))



        # #FRAUDE 1
        # if self.value() == 'stolen-card-1':
        #     return queryset.annotate(count_messages=Count('product__messages')).filter(Q(count_messages=0) & Q(total_amount__gte=100.00) & Q(started_at__lte=F('created_at') + timedelta(hours=1)))
        #     #Booking de plus de 100€ sans aucun message et qui a commencé 1heure apres avoir été bookée

        # #FRAUDE 2
        # if self.value() == 'stolen-card-2':
        #     return queryset.filter(Q(total_amount__gte=100.00) & Q(borrower__date_joined__gte=F('started_at') - timedelta(hours=3)) | Q(owner__date_joined__gte=F('started_at') - timedelta(hours=3)))
        #     #Booking de plus de 100€, dont le locataire ou le propriétaire a été crée moins de 3h avant le début de la location


class BookingAdmin(CurrentSiteAdmin):
    date_hierarchy = 'created_at'
    readonly_fields = ('borrower_profil_link', 'owner_profil_link', 'transaction_line')
    fieldsets = (
        (None, {'fields': ('state', 'product', 'started_at', 'ended_at')}),
        (_('Transaction'), {'fields': ('transaction_line',)}),
        (_('Borrower & Owner'), {'fields': (('borrower', 'borrower_profil_link'), ('owner', 'owner_profil_link'), 'ip')}),
        (_('Payment'), {'fields': ('total_amount', 'insurance_amount', 'deposit_amount', 'currency')}),
    )
    list_filter = ('started_at', 'ended_at', 'state', 'created_at', FraudeFilter)
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




















