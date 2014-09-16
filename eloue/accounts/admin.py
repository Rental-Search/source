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
from eloue.accounts.models import Patron, Pro, Address, PhoneNumber, PatronAccepted, ProPackage, Subscription, OpeningTimes, Billing
from eloue.accounts.forms import PatronChangeForm, PatronCreationForm

log = logbook.Logger('eloue')

class AddressInline(admin.TabularInline):
    model = Address
    extra = 0

class PhoneNumberInline(admin.TabularInline):
    model = PhoneNumber
    extra = 0

class OpeningTimesInline(admin.StackedInline):
    model = OpeningTimes

    fieldsets = (
        (_('Monday'), {'classes': ('collapse',), 'fields': ('monday_opens', 'monday_closes', 'monday_opens_second', 'monday_closes_second',)}),
        (_('Tuesday'), {'classes': ('collapse',), 'fields': ('tuesday_opens', 'tuesday_closes', 'tuesday_opens_second', 'tuesday_closes_second',)}),
        (_('Wednesday'), {'classes': ('collapse',), 'fields': ('wednesday_opens', 'wednesday_closes', 'wednesday_opens_second', 'wednesday_closes_second',)}),
        (_('Thursday'), {'classes': ('collapse',), 'fields': ('thursday_opens', 'thursday_closes', 'thursday_opens_second', 'thursday_closes_second',)}),
        (_('Friday'), {'classes': ('collapse',), 'fields': ('friday_opens', 'friday_closes', 'friday_opens_second', 'friday_closes_second',)}),
        (_('Saturday'), {'classes': ('collapse',), 'fields': ('saturday_opens', 'saturday_closes', 'saturday_opens_second', 'saturday_closes_second',)}),
        (_('Sunday'), {'classes': ('collapse',), 'fields': ('sunday_opens', 'sunday_closes', 'sunday_opens_second', 'sunday_closes_second',)}),
    )



class SubscriptionInline(admin.StackedInline):
    model = Subscription
    extra = 0
    readonly_fields = ('subscription_started', )
    fieldsets = (
        (None, {'fields': ('propackage', 'subscription_started', 'subscription_ended', 'free', 'number_of_free_month', 'payment_type', 'annual_payment_date', 'comment')}),
    )

class BillingInline(admin.TabularInline):
    model = Billing
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
    inlines = [AddressInline, PhoneNumberInline]
    actions = ['export_as_csv', 'send_activation_email']
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phones__number', 'addresses__city', 'company_name')

    def save_model(self, request, obj, form, change):
        obj.save()
        if not change:
            if obj.is_professional:
                obj.send_professional_activation_email()
    
    def export_as_csv(self, request, queryset):
        response = HttpResponse(mimetype='text/csv')
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
    

class AddressAdmin(admin.ModelAdmin):
    list_display = ('patron', 'address1', 'address2', 'zipcode', 'city', 'country', 'is_geocoded')
    list_filter = ('country',)
    save_on_top = True
    search_fields = ('patron__username', 'address1', 'address2', 'zipcode', 'city')
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



class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'propackage', 'subscription_started', 'subscription_ended', 'payment_type','online_date', 'comment',)
    raw_id_fields = ("patron",)
    readonly_fields = ('subscription_started', 'company_name', 'contact', 'address', 'phone', 'online_date', 'products_count', 'email', 'slimpay_code')
    fieldsets = (
        (_('Abonnement'), {'fields': ('propackage', 'subscription_started', 'subscription_ended', 'payment_type', 'annual_payment_date', 'free', 'number_of_free_month', 'comment',)}),
        (_('Patron informations'), {'fields': ('patron', 'company_name', 'contact', 'address', 'phone', 'online_date', 'products_count', 'email', 'slimpay_code',)}),
    )
    ordering = ['-subscription_started']
    list_filter = ('payment_type', 'propackage',)
    search_fields = ('company_name', 'patron__username',)

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
            slimpay = obj.patron.slimpaymandateinformation_set.all()
            return slimpay[0].RUM
        except:
            return None


class ProAdmin(PatronAdmin):
    list_display = ('company_name', 'last_subscription', 'last_subscription_started_date', 'last_subscription_ended_date',)
    list_filter = ()
    inlines = [AddressInline, PhoneNumberInline, OpeningTimesInline, SubscriptionInline]

    def queryset(self, request):
        return Pro.objects.exclude(subscriptions=None)

    def last_subscription(self, obj):
        return obj.subscription_set.all().order_by('-subscription_started')[0].propackage

    def last_subscription_started_date(self, obj):
        return obj.subscription_set.all().order_by('-subscription_started')[0].subscription_started

    def last_subscription_ended_date(self, obj):
        return obj.subscription_set.all().order_by('-subscription_started')[0].subscription_ended


try:
    admin.site.register(Address, AddressAdmin)
    admin.site.register(PhoneNumber, PhoneNumberAdmin)
    admin.site.register(Patron, PatronAdmin)
    admin.site.register(Pro, ProAdmin)
    admin.site.register(PatronAccepted)
    admin.site.register(ProPackage)
    admin.site.register(Subscription, SubscriptionAdmin)
except admin.sites.AlreadyRegistered, e:
    log.warn('Site is already registered : %s' % e)
