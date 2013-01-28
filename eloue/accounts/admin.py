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
from eloue.accounts.models import Patron, Address, PhoneNumber, PatronAccepted, ProPackage, Subscription
from eloue.accounts.forms import PatronChangeForm, PatronCreationForm

log = logbook.Logger('eloue')

class AddressInline(admin.TabularInline):
    model = Address


class PhoneNumberInline(admin.TabularInline):
    model = PhoneNumber


class PatronAdmin(UserAdmin, CurrentSiteAdmin):
    form = PatronChangeForm
    add_form = PatronCreationForm
    fieldsets = (
        (None, {'fields': ('username', 'slug', 'password', 'sites')}),
        (_('Personal info'), {'fields': ('civility', 'first_name', 'last_name', 'email', 'affiliate')}),
        (_('Company info'), {'fields': ('is_professional', 'company_name')}),
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
    search_fields = ('address1', 'address2', 'zipcode', 'city')
    fieldsets = (
        (None, {'fields': ('address1', 'address2', 'zipcode', 'city')}),
        (_('Geolocation'), {'classes': ('collapse',), 'fields': ('position',)})
    )

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('patron', 'propackage', 'subscription_started', 'subscription_ended')
    raw_id_fields = ("patron",)


class ProPackageAdmin(admin.ModelAdmin):
    pass


try:
    admin.site.register(Address, AddressAdmin)
    admin.site.register(Patron, PatronAdmin)
    admin.site.register(PatronAccepted)
    admin.site.register(ProPackage, ProPackageAdmin)
    admin.site.register(Subscription, SubscriptionAdmin)
except admin.sites.AlreadyRegistered, e:
    log.warn('Site is already registered : %s' % e)
