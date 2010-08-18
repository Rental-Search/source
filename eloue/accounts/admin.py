# -*- coding: utf-8 -*-
import smtplib

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from eloue.accounts.models import Patron
from eloue.accounts.forms import PatronChangeForm

class PatronAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_staff', 'is_active', 'is_superuser', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Groups'), {'classes': ('collapse',), 'fields': ('groups',)}),
    )
    list_display = ('username', 'email', 'is_staff', 'is_active', 'is_expired', 'date_joined')
    date_hierarchy = 'date_joined'
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    save_on_top = True
    ordering = ['-date_joined']
    form = PatronChangeForm
    actions = ['send_activation_email']
    
    def send_activation_email(self, request, queryset):
        for patron in queryset:
            if patron.is_expired() or patron.is_active:
                continue
            try:
                patron.send_activation_email()
            except smtplib.SMTPException:
                pass
    send_activation_email.short_description = _(u"Envoyer à nouveau l'email d'activation")
    

admin.site.register(Patron, PatronAdmin)