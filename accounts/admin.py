# -*- coding: utf-8 -*-
import csv
import smtplib
import logbook

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.utils.translation import ugettext_lazy as _

from eloue.admin import CurrentSiteAdmin
from accounts.models import Patron, Address, PhoneNumber, PatronAccepted, ProPackage, Subscription, OpeningTimes, Billing, ProAgency
from accounts.forms import PatronChangeForm, PatronCreationForm
from products.models import Product

log = logbook.Logger('eloue')

class AddressInline(admin.TabularInline):
    model = Address
    extra = 0

class PhoneNumberInline(admin.TabularInline):
    model = PhoneNumber
    extra = 0

class OpeningTimesInline(admin.StackedInline):
    model = OpeningTimes
    extra = 0

class BillingInline(admin.StackedInline):
    model = Billing

class ProAgencyInline(admin.TabularInline):
    model = ProAgency
    extra = 0


class PatronAdmin(UserAdmin, CurrentSiteAdmin):
    form = PatronChangeForm
    add_form = PatronCreationForm
    fieldsets = (
        (None, {'fields': ('username', 'slug', 'password', 'sites')}),
        (_('Personal info'), {'fields': ('civility', 'first_name', 'last_name', 'email', 'affiliate', 'avatar', 'about')}),
        (_('Company info'), {'fields': ('is_professional', 'company_name', 'url')}),
        (_('Permissions'), {'fields': ('is_staff', 'is_active', 'is_superuser', 'is_subscribed', 'new_messages_alerted', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined',)}),

        (_('Paypal'), {'classes': ('collapse',), 'fields': ('paypal_email',)}),
        (_('Groups'), {'classes': ('collapse',), 'fields': ('groups',)}),
    )

    add_fieldsets = (
        (None, {'fields': ('username', 'slug','password1', 'password2', 'sites')}),
        (_('Personal info'), {'fields': ('civility', 'first_name', 'last_name', 'email', 'affiliate')}),
        (_('Company info'), {'fields': ('is_professional', 'company_name')}),
        (_('Permissions'), {'fields': ('is_subscribed', 'new_messages_alerted')}),
    )

    list_display = ('username', 'first_name', 'last_name', 'email', 'company_name',
        'is_staff', 'is_active', 'is_expired', 'is_professional', 'is_subscribed', 'date_joined', 'modified_at', 'new_messages_alerted')
    date_hierarchy = 'date_joined'
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'is_professional', 'is_subscribed', 'affiliate', 'new_messages_alerted')
    save_on_top = True
    ordering = ['-date_joined']
    inlines = [AddressInline, PhoneNumberInline, OpeningTimesInline, ProAgencyInline]
    actions = ['export_as_csv', 'send_activation_email', 'index_user_products', 'unindex_user_products']
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phones__number', 'addresses__city', 'company_name')

    def save_model(self, request, obj, form, change):
        obj.save()
        if not change:
            if obj.is_professional:
                obj.send_professional_activation_email()
    
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % self.model._meta.db_table
        w = csv.writer(response, delimiter=',')
        for obj in queryset:
            w.writerow([smart_str(getattr(obj, field.name)) for field in self.model._meta.fields])
        return response
    export_as_csv.short_description = _(u"Exporter en csv")
    
    def send_activation_email(self, request, queryset):
        for patron in queryset:
            if patron.is_active:
                continue
            try:
                patron.send_activation_email()
            except smtplib.SMTPException:
                pass
    send_activation_email.short_description = _(u"Envoyer à nouveau l'email d'activation")

    def index_user_products(self, request, queryset):
        for user in queryset:
            products = Product.objects.filter(owner=user)
            for p in products:
                p.is_allowed = True
                p.save()
    index_user_products.short_description = _(u"Indexer les produits")

    def unindex_user_products(self, request, queryset):
       for user in queryset:
            products = Product.objects.filter(owner=user)
            for p in products:
                p.is_allowed = False
                p.save()
    unindex_user_products.short_description = _(u"Désindexer les produits")
    

class AddressAdmin(admin.ModelAdmin):
    list_display = ('patron', 'address1', 'address2', 'zipcode', 'city', 'country', 'is_geocoded')
    list_filter = ('country',)
    save_on_top = True
    search_fields = ('address1', 'address2', 'zipcode', 'city')
    fieldsets = (
        (None, {'fields': ('address1', 'address2', 'zipcode', 'city')}),
        (_('Geolocation'), {'classes': ('collapse',), 'fields': ('position',)})
    )


class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ('patron', 'number')
    search_fields = ('patron__username', 'number')
    readonly_fields = ('patron', )
    fieldsets = (
        (None, {'fields': ('patron', 'number', 'kind')}),
    )


class SlimpayFilter(admin.SimpleListFilter):
    title = _('Signature')

    parameter_name = 'slimpay_code'

    def lookups(self, request, model_admin):
        return (
            ('true', _('Avec signature')),
            ('false', _('Sans signature'))
        )

    def queryset(self, request, queryset):
        if self.value() == 'true':
            return queryset.filter(patron__slimpaymandateinformation__transactionStatus='success').exclude(patron__slimpaymandateinformation__transactionStatus='failure').distinct()
        if self.value() == 'false':
            return queryset.filter(patron__slimpaymandateinformation__transactionStatus='failure').exclude(patron__slimpaymandateinformation__transactionStatus='success').distinct()


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'propackage', 'slimpay_code', 'subscription_started', 'subscription_ended', 'payment_type','online_date', 'comment',)
    raw_id_fields = ("patron",)
    readonly_fields = ('subscription_started', 'company_name', 'contact', 'address', 'phone', 'online_date', 'products_count', 'email', 'slimpay_code', 'slimpay_link')
    fieldsets = (
        (_('Abonnement'), {'fields': ('propackage', 'subscription_started', 'subscription_ended', 'payment_type', 'annual_payment_date', 'free', 'number_of_free_month', 'comment',)}),
        (_('Patron informations'), {'fields': ('patron', 'company_name', 'contact', 'address', 'phone', 'online_date', 'products_count', 'email', 'slimpay_code', 'slimpay_link',)}),
    )
    date_hierarchy = 'subscription_started'
    ordering = ['-subscription_started']
    list_filter = ('payment_type', 'propackage', SlimpayFilter)
    search_fields = ('patron__username', 'patron__email', 'patron__company_name')

    def company_name(self, obj):
        return obj.patron.company_name

    def contact(self, obj):
        return '%s %s' % (obj.patron.first_name, obj.patron.last_name)

    def address(self, obj):
        return obj.patron.default_address

    def phone(self, obj):
        return obj.patron.default_number

    def email(self, obj):
        return obj.patron.email

    def online_date(self, obj):
        try:
            return obj.patron.products.all().order_by('-created_at')[0].created_at.strftime("%d/%m/%y")
        except:
            return None

    def products_count(self, obj):
        return obj.patron.products.all().count()

    def slimpay_code(self, obj):
        try:
            slimpay = obj.patron.slimpaymandateinformation_set.latest('pk')
            return slimpay.RUM
        except:
            return None

    def slimpay_link(self, obj):
        slimpay_link = '<a href="/edit/accounts/slimpay/%s/"">Ajouter un iban</a>' % obj.patron.pk
        return slimpay_link

    slimpay_link.allow_tags = True


class ProPackageAdmin(admin.ModelAdmin):
    pass


class ProAgencyAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'name', 'address1', 'address2', 'zipcode', 'city', 'country',)

    search_fields = ('patron__company_name', 'name',)

    raw_id_fields = ('patron',)

    def company_name(self, obj):
        if obj.patron.company_name:
            return obj.patron.company_name
        else:
            return obj.patron.username


try:
    admin.site.register(Address, AddressAdmin)
    admin.site.register(PhoneNumber, PhoneNumberAdmin)
    admin.site.register(Patron, PatronAdmin)
    admin.site.register(PatronAccepted)
    admin.site.register(ProPackage, ProPackageAdmin)
    admin.site.register(Subscription, SubscriptionAdmin)
    admin.site.register(ProAgency, ProAgencyAdmin)
except admin.sites.AlreadyRegistered, e:
    log.warn('Site is already registered : %s' % e)
