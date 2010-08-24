# -*- coding: utf-8 -*-
import smtplib

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from eloue.accounts.models import Patron, Address, PhoneNumber, Comment
from eloue.accounts.forms import PatronChangeForm

class AddressInline(admin.TabularInline):
    model = Address

class PhoneNumberInline(admin.TabularInline):
    model = PhoneNumber

class PatronAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('civility', 'first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_staff', 'is_active', 'is_superuser', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Groups'), {'classes': ('collapse',), 'fields': ('groups',)}),
    )
    list_display = ('username', 'email', 'company_name', 'is_staff', 'is_active', 'is_expired', 'is_professional', 'date_joined', 'modified_at')
    date_hierarchy = 'date_joined'
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'is_professional')
    save_on_top = True
    ordering = ['-date_joined']
    inlines = [ AddressInline, PhoneNumberInline ]
    form = PatronChangeForm
    actions = ['send_activation_email']
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phones__number', 'addresses__city', 'company_name')
    
    def send_activation_email(self, request, queryset):
        for patron in queryset:
            if patron.is_expired() or patron.is_active:
                continue
            try:
                patron.send_activation_email()
            except smtplib.SMTPException:
                pass
    send_activation_email.short_description = _(u"Envoyer à nouveau l'email d'activation")
    

class CommentAdmin(admin.ModelAdmin):
    pass

class AddressAdmin(admin.ModelAdmin):
    list_display = ('address1', 'address2', 'city', 'country')
    list_filter = ('country',)
    save_on_top = True
    search_fields = ('address1', 'address2', 'zipcode', 'city')
    fieldsets = (
        (None, {'fields':('address1', 'address2', 'zipcode', 'city')}),
        (_('Geolocation'), {'classes':('collapse',), 'fields':('position',)})
    )

admin.site.register(Address, AddressAdmin)
admin.site.register(Patron, PatronAdmin)
admin.site.register(Comment, CommentAdmin)