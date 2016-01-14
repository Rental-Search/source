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
            ('filtre-1', _('1er TRI')),
            ('joined-created', _('inscrip_prop<demande+2j')),
            ('joined-joined', _('inscr_prop+/-1j inscr_loc')),
            ('requ_accept', _('demande>acceptation-15min')),
            ('book_requ', _('demande_loc>2 (en_attente,a_venir,en_cours)')),
            
        )
    def queryset(self, request, queryset):
        #1er TRI
        if self.value() == 'filtre-1':
            return queryset.annotate(count_bookings=Count('borrower__rentals')).filter(Q(total_amount__gte=100.00) | Q(started_at__lte=F('created_at') + timedelta(hours=1)) & Q(total_amount__gte=50.00) | Q(owner__email__icontains='outlook') | Q(borrower__email__icontains='outlook') | Q(Q(borrower__date_joined__gte=F('owner__date_joined') - timedelta(days=1)) & Q(borrower__date_joined__lte=F('owner__date_joined') + timedelta(days=1))) | Q(owner__date_joined__gte=F('created_at') - timedelta(days=2)) | Q(Q(count_bookings__gte=3) & Q(Q(state=BOOKING_STATE.AUTHORIZED) | Q(state=BOOKING_STATE.PENDING))))
            #Bookings de plus de 100€ OU de plus de 50€ et ayant commencé moins de 1h après sa création OU avec un locataire ou propriétaire avec email outlook OU dont le propriétaire et locataire se sont inscrits à moins de 1jour d'interval OU dont le propriétaire s'est inscrit moins de 2 jours avant la création de la location
        
        #loc_creation<owner_joined+2j
        if self.value() == 'joined-created':
            return queryset.filter(Q(owner__date_joined__gte=F('created_at') - timedelta(days=2)))

        #borrower_joined= +/- 1j owner_joined
        if self.value() == 'joined-joined':
            return queryset.filter(Q(borrower__date_joined__gte=F('owner__date_joined') - timedelta(days=1)) & Q(borrower__date_joined__lte=F('owner__date_joined') + timedelta(days=1)))

        #demande>acceptation-15min
        if self.value() == 'requ_accept':
            bookinglogs = BookingLog.objects.filter(Q(source_state=BOOKING_STATE.AUTHORIZED) & Q(target_state=BOOKING_STATE.PENDING) & Q(created_at__lte=F('booking__created_at') + timedelta(minutes=15)))
            return queryset.filter(pk__in=[bookinglog.booking.pk for bookinglog in bookinglogs])
        
        #borrower_book-requ>2(en_attente,a_venir,en_cours)
        if self.value() == 'book_requ':
            return queryset.annotate(count_bookings=Count('borrower__rentals')).filter(Q(count_bookings__gte=2) & Q(Q(state=BOOKING_STATE.AUTHORIZED) | Q(state=BOOKING_STATE.PENDING) | Q(state=BOOKING_STATE.ONGOING)))
        
        
class BookingAdmin(CurrentSiteAdmin):
    date_hierarchy = 'created_at'
    readonly_fields = ('borrower_profil_link', 'owner_profil_link', 'transaction_line')
    fieldsets = (
        (None, {'fields': ('state', 'product', 'started_at', 'ended_at')}),
        (_('Transaction'), {'fields': ('transaction_line',)}),
        (_('Borrower & Owner'), {'fields': (('borrower', 'borrower_profil_link'), ('owner', 'owner_profil_link'), 'ip')}),
        (_('Payment'), {'fields': ('total_amount', 'insurance_amount', 'deposit_amount', 'currency')}),
    )
    list_filter = (FraudeFilter, 'created_at','state', 'started_at', 'ended_at')
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




















