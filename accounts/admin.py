# -*- coding: utf-8 -*-
import csv
import smtplib
import logbook

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site

from eloue.admin import CurrentSiteAdmin
from accounts.models import Patron, Pro, Address, PhoneNumber, PatronAccepted, ProPackage, Subscription, OpeningTimes, Billing, ProAgency, ProReport, Ticket
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

class SubscriptionInline(admin.StackedInline):
    model = Subscription
    extra = 0
    fieldsets = (
        (None, {'fields': ('seller', 'propackage', 'signed_at', 'subscription_started', 'subscription_ended','amount', 'fee', 'free', 'number_of_free_month', 'payment_type', 'comment')}),
    )

class ProReportInline(admin.TabularInline):
    readonly_fields = ('agent',)
    model = ProReport
    extra = 0
    fk_name = 'pro'

class ProTicketInline(admin.TabularInline):
    readonly_fields = ('agent',)
    model = Ticket
    extra = 0
    fk_name = 'pro'

class PatronAdmin(UserAdmin, CurrentSiteAdmin):
    form = PatronChangeForm
    add_form = PatronCreationForm
    readonly_fields = ('profil_link', 'owner_products', 'owner_car_products', 'owner_realestate_products', 'bookings_link', 'messages_link')
    fieldsets = (
        (_('Personal info'), {'fields': ('email', 'civility', 'first_name', 'last_name','last_login', 'date_joined','password')}),
        (_('Profile'), {'fields': ('username', 'slug', 'avatar',  'about', 'sites')}),
        (_('Bookings'), {'fields': ('bookings_link',)}),
        (_('Products'), {'fields': ('profil_link', 'owner_products','owner_car_products','owner_realestate_products',)}),
        (_('Messages'), {'fields': ('messages_link',)}),
        (_('Company info'), {'fields': ('is_professional', 'company_name', 'url')}),
        (_('Permissions'), {
            'classes': ('collapse',),
            'fields': ('is_staff', 'is_active', 'is_superuser', 'is_subscribed', 'new_messages_alerted', 'user_permissions')
        }),
    )

    add_fieldsets = (
        (None, {'fields': ('username', 'slug','password1', 'password2', 'sites')}),
        (_('Personal info'), {'fields': ('civility', 'first_name', 'last_name', 'email', 'affiliate')}),
        (_('Company info'), {'fields': ('is_professional', 'company_name')}),
        (_('Permissions'), {'fields': ('is_subscribed', 'new_messages_alerted')}),
    )

    list_display = ('username', 'first_name', 'last_name', 'email', 'company_name',
        'is_staff', 'is_active', 'is_expired', 'is_professional', 'is_subscribed', 'date_joined', 'modified_at', 'new_messages_alerted')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'is_professional', 'is_subscribed', 'affiliate', 'new_messages_alerted')
    save_on_top = True
    ordering = ['-date_joined']
    inlines = [AddressInline, PhoneNumberInline, OpeningTimesInline, ProAgencyInline]
    actions = ['export_as_csv', 'send_activation_email', 'index_user_products', 'unindex_user_products']
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phones__number', 'addresses__city', 'company_name')


    def bookings_link (self, obj):
        email = obj.email
        bookings_link = '<a href="http://localhost:8000/edit/rent/booking?q=%s" target="_blank">Lien vers les bookings</a>' % email
        return bookings_link
    bookings_link.allow_tags = True
    bookings_link.short_description = _(u"lien vers les bookings")

    def profil_link(self, obj):
        profil_link = '<a href="%s" target="_blank">Lien vers le profil</a>' % obj.get_absolute_url()
        return profil_link   
    profil_link.allow_tags = True
    profil_link.short_description = _(u"lien profil")

    def products_count(self, obj):
        return obj.products.all().count()
    products_count.short_description = _(u"nombre d'annonce")

    def owner_products (self, obj):
        owner_product = '<a href="http://localhost:8000/edit/products/product/?q=%s" target="_blank">Lien vers les annonces</a>' % obj.pk
        return owner_product
    owner_products.allow_tags = True
    owner_products.short_description = _(u"annonces")

    def owner_car_products (self, obj):
        owner_car_product = '<a href="http://localhost:8000/edit/products/carproduct/?q=%s" target="_blank">Lien vers les annonces de voiture</a>' % obj.pk
        return owner_car_product
    owner_car_products.allow_tags = True
    owner_car_products.short_description = _(u"annonces de voiture")

    def owner_realestate_products (self, obj):
        owner_realestate_product = '<a href="http://localhost:8000/edit/products/realestateproduct/?q=%s" target="_blank">Lien vers les annonces de logement</a>' % obj.pk
        return owner_realestate_product
    owner_realestate_products.allow_tags = True
    owner_realestate_products.short_description = _(u"annonces de logements")

    def messages_link (self, obj):
        username = obj.username
        messages_link = '<a href="http://localhost:8000/edit/django_messages/message/?q=%s" target="_blank">Lien vers les messages</a>' % username
        return messages_link
    messages_link.allow_tags = True
    messages_link.short_description = _(u"lien vers les messages")

    

    def queryset(self, request):
        current_site = Site.objects.get_current()
        if current_site.pk == 1:
            return super(PatronAdmin, self).queryset(request)
        else:
            return super(PatronAdmin, self).queryset(request).filter(source=current_site)

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
    fieldsets = (
        (None, {'fields': ('patron', 'number', 'kind')}),
    )
    raw_id_fields = ("patron",)


    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('patron', )
        return self.readonly_fields


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


class ProAdmin(PatronAdmin):
    list_display = ('company_name', 'closed_ticket', 'last_report_date', 'last_subscription', 'last_subscription_started_date', 'last_subscription_ended_date',)
    list_filter = ()
    inlines = [SubscriptionInline, ProReportInline, ProTicketInline, OpeningTimesInline, PhoneNumberInline, AddressInline,]
    readonly_fields = ('store_link', 'products_count', 'edit_product_link', 'closed_ticket',)
    fieldsets = (
        (_('Company info'), {'fields': ('company_name', 'civility', 'first_name', 'last_name', 'username', 'is_professional', 'password')}),
        (_('Contact'), {'fields': ('email', 'default_number', 'default_address', 'url')}),
        (_('Boutique'), {'fields': ('store_link', 'edit_product_link', 'products_count', 'slug', 'avatar',  'about', 'sites')}),
        (_('Permissions'), {
            'classes': ('collapse',),
            'fields': ('is_staff', 'is_active', 'is_superuser', 'is_subscribed', 'new_messages_alerted', 'user_permissions')
        }),
    )
    date_hierarchy = None
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phones__number', 'addresses__city', 'company_name', 'pk',)

    def queryset(self, request):
        return Pro.objects.exclude(subscriptions=None)

    def get_form(self, request, obj=None, **kwargs):
        form = super(ProAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['default_number'].queryset = form.base_fields['default_number'].queryset.filter(patron=obj)
        form.base_fields['default_address'].queryset = form.base_fields['default_address'].queryset.filter(patron=obj)
        return form

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            try:
                instance.agent = request.user
                instance.save()
            except:
                pass
        formset.save_m2m()

    def store_link(self, obj):
        store_link = '<a href="%s" target="_blank">Voir la boutique</a>' % obj.get_absolute_url()
        return store_link   
    store_link.allow_tags = True
    store_link.short_description = _(u"lien boutique")

    def products_count(self, obj):
        return obj.products.all().count()
    products_count.short_description = _(u"nombre d'annonce")

    def edit_product_link(self, obj):
        edit_product_link = '<a href="/edit/products/product/?q=%s" target="_blank">Editer les annonces</a>' % obj.pk
        return edit_product_link
    edit_product_link.allow_tags = True
    edit_product_link.short_description = _(u"annonces")

    def last_subscription(self, obj):
        last_subscription = obj.subscription_set.all().order_by('-subscription_started')[0]
        if last_subscription.fee:
            return "%s : %s : %s" % (last_subscription.propackage.name, last_subscription.amount, last_subscription.fee)
        else:
            return "%s : %s" % (last_subscription.propackage.name, last_subscription.amount)
    last_subscription.short_description = _(u"Souscription")

    def last_subscription_started_date(self, obj):
        return obj.subscription_set.all().order_by('-subscription_started')[0].subscription_started
    last_subscription_started_date.short_description = _(u"mise en lignes")

    def last_subscription_ended_date(self, obj):
        return obj.subscription_set.all().order_by('-subscription_started')[0].subscription_ended
    last_subscription_ended_date.short_description = _(u"fin de souscription")

    def last_report_date(self, obj):
        last_report = obj.reports.latest('created_at')
        return last_report.created_at
    last_report_date.short_description = _(u"dernier rapport")

    def closed_ticket(self, obj):
        tickets = obj.tickets.filter(is_closed=False)
        if not tickets:
            return True
        else:
            return False
    closed_ticket.short_description = _(u"tickets résolus")
    closed_ticket.boolean = True


try:
    admin.site.register(Address, AddressAdmin)
    admin.site.register(PhoneNumber, PhoneNumberAdmin)
    admin.site.register(Patron, PatronAdmin)
    admin.site.register(PatronAccepted)
    admin.site.register(ProPackage, ProPackageAdmin)
    admin.site.register(Subscription, SubscriptionAdmin)
    admin.site.register(ProAgency, ProAgencyAdmin)
    admin.site.register(Pro, ProAdmin)
except admin.sites.AlreadyRegistered, e:
    log.warn('Site is already registered : %s' % e)
