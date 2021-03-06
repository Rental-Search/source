# -*- coding: utf-8 -*-
import decimal
import logbook

from django.utils.translation import gettext_lazy as _
from django.contrib import admin, messages
from django.shortcuts import redirect
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site

from mptt.admin import MPTTModelAdmin
from mptt.forms import TreeNodeChoiceField

from django_messages.models import Message
from django_messages.admin import MessageAdmin
from django import forms

from modeltranslation.admin import TranslationAdmin

from products.forms import ProductAdminForm
from products.models import Alert, Product, CarProduct, RealEstateProduct, Picture, Category, Property, PropertyValue, Price, ProductReview, PatronReview, Curiosity, ProductRelatedMessage

from eloue.admin import CurrentSiteAdmin

from import_export import resources, widgets, fields
from import_export.admin import ImportMixin
from products.choices import UNIT
from import_export.formats import base_formats
from django.core.management import call_command
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.views.decorators import staff_member_required
from django.conf.urls import patterns, url
from queued_search.utils import get_queue_name
from queues import queues

log = logbook.Logger('eloue')


class PictureInline(admin.TabularInline):
    model = Picture


class PropertyValueInline(admin.TabularInline):
    model = PropertyValue


class PriceInline(admin.TabularInline):
    model = Price

def convert_to_carproduct(modeladmin, request, queryset):
    import datetime
    if len(queryset) != 1:
        messages.error(request, 'bulk action is not allowed')
        return
    product = queryset[0]
    if product.name != 'product':
        messages.error(request, 'this action can only be called for normal products')
        return
    carproduct = CarProduct(
        product_ptr=product,deposit_amount=decimal.Decimal(2000), 
        tax_horsepower=5, first_registration_date=datetime.date(2011, 1, 1)
    )
    carproduct.save_base(raw=True)
    return redirect('admin:products_carproduct_change', carproduct.pk)
convert_to_carproduct.short_description = "Convert selected products to CarProduct"


def convert_to_realestateproduct(modeladmin, request, queryset):
    realestateproduct = None
    if len(queryset) != 1:
        messages.error(request, 'bulk action is not allowed')
        return
    product = queryset[0]
    if product.name != 'product':
        messages.error(request, 'this action can only be called for normal products')
        return
    realestateproduct = RealEstateProduct(product_ptr=product)
    realestateproduct.save_base(raw=True)
    return redirect('admin:products_realestateproduct_change', realestateproduct.pk)
convert_to_realestateproduct.short_description = "Convert selected products to RealEstateProduct"

class ProductCurrentSiteAdmin(CurrentSiteAdmin):
    date_hierarchy = 'created_at'
    search_fields = ['summary', 'description', 'category__name', 'owner__username', 'owner__email']
    inlines = [PictureInline, PropertyValueInline, PriceInline]
    raw_id_fields = ("owner", "address", "phone")
    list_display = ('summary', 'category', 'deposit_amount', 'quantity', 'is_archived', 'shipping', 'created_at', 'modified_at')
    list_filter = ('shipping', 'is_archived', 'is_allowed', 'category')
    list_editable = ('category',)
    ordering = ['-created_at']
    list_per_page = 20
    form = ProductAdminForm


PRICE_FIELDS=['price_hour',
                    'price_day',
                    'price_three_days',
                    'price_week',
                    'price_fifteen_days',
                    'price_month',]


class ProductResource(resources.ModelResource):
    
    price_hour = fields.Field(widget=widgets.DecimalWidget())
    price_day = fields.Field(widget=widgets.DecimalWidget())
    price_three_days = fields.Field(widget=widgets.DecimalWidget())
    price_week = fields.Field(widget=widgets.DecimalWidget())
    price_fifteen_days = fields.Field(widget=widgets.DecimalWidget())
    price_month = fields.Field(widget=widgets.DecimalWidget())
    
     
    class Meta:
        model = Product
        report_skipped = True
        use_transactions = True
        fields = ['id', 'summary', 'description', 'category', 'sites',
                   'deposit_amount', 'currency', 'owner', ] + PRICE_FIELDS
    
    
    def __init__(self, *args, **kwargs):
        super(ProductResource, self).__init__(*args, **kwargs)
        self._prices = []
    
    
    def import_obj(self, obj, data, dry_run):
        super(ProductResource, self).import_obj(obj, data, dry_run)
        prices = []
        for f in PRICE_FIELDS:
            amount = self.fields[f].clean(data)
            if amount is None:
                continue
            unit = f.split('_', 1)[1].upper()
            prices.append(Price(amount=amount, unit=UNIT[unit]))
        self._prices = prices
    
            
    def before_save_instance(self, instance, dry_run):
        owner = instance.owner
        instance.phone = owner.default_number
        instance.address = owner.default_address
    
        
    def after_save_instance(self, instance, dry_run):
        if not dry_run and len(self._prices)>0:
            instance.prices = self._prices
        
        
        
class ProductAdmin(ImportMixin, ProductCurrentSiteAdmin):
    date_hierarchy = 'created_at'
    search_fields = ['summary', 'description', 'category__name', 'owner__username', 'owner__email', 'owner__pk']
    inlines = [PictureInline, PropertyValueInline, PriceInline]
    raw_id_fields = ("owner", "address", "phone")
    readonly_fields = ('is_pro', 'user_link', 'import_record', 'original_id')
    list_display = ('summary', 'is_pro','user_link', 'category', 'deposit_amount', 'quantity', 'is_archived', 'shipping', 'created_at', 'modified_at')
    list_filter = ('shipping', 'is_archived', 'is_allowed', 'category')
    list_editable = ('category',)
    ordering = ['-created_at']
    list_per_page = 20
    form = ProductAdminForm
    actions = [convert_to_carproduct, convert_to_realestateproduct]
    resource_class = ProductResource
    change_list_template = "admin/products/change_list.html"
    formats = (
        base_formats.XLSX,
        base_formats.XLS,
    )

    MESSAGE_REINDEX_SUCCESS = _("Index updated")
    
    def get_urls(self):
        urls = super(ProductAdmin, self).get_urls()    
        custom_urls = patterns("",
                               url(r"^update_index/$", 
                               self.admin_site.admin_view(self.update_index), 
                               name="update_product_index")) 
        custom_urls += urls
        return custom_urls
    
    
    def update_index(self, request):
        
        queue = queues.Queue(get_queue_name())
        
        init_len = len(queue)
        
        if not init_len:
            self.message_user(request, "Nothing to re-index",
                  level=messages.WARNING)
            return redirect("admin:products_product_changelist")
        
        try:
            call_command("process_search_queue")
                    
            final_len = len(queue)
            
            if init_len == final_len:
                raise Exception("No objects were re-indexed" % final_len)
            
            self.message_user(request, self.MESSAGE_REINDEX_SUCCESS,
                              level=messages.SUCCESS)
            
            LogEntry.objects.log_action(
                user_id = request.user.id,
                content_type_id = ContentType.objects.get_for_model(Product).pk,
                object_id = None,
                object_repr = "Re-indexed %d objects" % (init_len - final_len),
                action_flag = CHANGE,
                change_message = 'Objects re-indexed')
        
        except Exception as e:
            self.message_user(request, str(e),
                          level=messages.ERROR)
            
        return redirect("admin:products_product_changelist")
    

    def is_pro(self, obj):
        if obj.owner.current_subscription != None:
            is_pro = _("Professionnel") 
        else:
            is_pro = _("Particulier")
        return is_pro
    is_pro.allow_tags = True
    is_pro.short_description = _(u"Pro ou Part")

    def user_link(self, obj):
        user = obj.owner
        user_link = '<a href="/edit/accounts/patron/%s" target="_blank">Lien vers la page du proprietaire</a>' % user.pk
        return _(user_link) 
    user_link.allow_tags = True
    user_link.short_description = _(u"Proprietaire")

    def queryset(self, request):
        qs = super(ProductAdmin, self).queryset(request).filter(carproduct=None, realestateproduct=None)
        current_site = Site.objects.get_current()
        
        if current_site.pk == 1:
            return qs
        else:
            return qs.filter(source=current_site)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'category':
            kwargs['form_class'] = TreeNodeChoiceField
            kwargs['empty_label'] = u"Choisissez une catégorie"
            kwargs['level_indicator'] = u"--"
            kwargs['queryset'] = Category.tree.all()
        return super(ProductAdmin, self).formfield_for_dbfield(db_field, **kwargs)


class ProductOwner(ProductCurrentSiteAdmin):
    def function():
        pass
class RealEstateProductAdmin(ProductCurrentSiteAdmin):

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'category':
            kwargs['form_class'] = TreeNodeChoiceField
            kwargs['empty_label'] = u"Choisissez une catégorie"
            kwargs['level_indicator'] = u"--"
            kwargs['queryset'] = Category.tree.get(name=u'Location saisonnière').get_descendants()
        return super(RealEstateProductAdmin, self).formfield_for_dbfield(db_field, **kwargs)

class CarProductAdmin(ProductCurrentSiteAdmin):
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'category':
            kwargs['form_class'] = TreeNodeChoiceField
            kwargs['empty_label'] = u"Choisissez une catégorie"
            kwargs['level_indicator'] = u"--"
            kwargs['queryset'] = Category.tree.get(name=u'Automobile').get_descendants()
        return super(CarProductAdmin, self).formfield_for_dbfield(db_field, **kwargs)


class CategoryAdmin(MPTTModelAdmin, TranslationAdmin):
    list_display = ('name', 'parent')
    search_fields = ['name', 'parent__name']
    prepopulated_fields = {"slug": ("name",)}
    raw_id_fields = ("product",)



class PropertyAdmin(admin.ModelAdmin):
    fieldsets = ((None, {'fields': (('attr_name', 'category', 'value_type'), 'name', 'default_str', 'choices_str', 'faceted'),}),
                 (u"Propriétés numériques", {'fields': ('min_str', 'max_str'),}))
    list_display = ('name', 'attr_name', 'category', 'value_type', 'faceted')


class ProductReviewAdmin(admin.ModelAdmin):
    raw_id_fields = ("reviewer", "product")


class PatronReviewAdmin(admin.ModelAdmin):
    raw_id_fields = ("reviewer", "patron")


class CuriosityAdmin(CurrentSiteAdmin):
    list_display = ('product',)
    raw_id_fields = ("product",)

class AlertAdmin(admin.ModelAdmin):
    pass


class EloueMessageAdminForm(forms.ModelForm):
    """
    Custom AdminForm to enable messages to groups and all users.
    """
    group = forms.ChoiceField(label=_('group'), required=False,
        help_text=_('Creates the message optionally for all users or a group of users.'))

    def __init__(self, *args, **kwargs):
        super(EloueMessageAdminForm, self).__init__(*args, **kwargs)
        self.fields['group'].choices = self._get_group_choices()
        #self.fields['recipient'].required = True

    def _get_group_choices(self):
        return [('', u'---------'), ('all', _('All users'))] + \
            [(group.pk, group.name) for group in Group.objects.all()]

    class Meta:
        model = Message
        fields = ('sender', 'recipient', 'group', 'parent_msg', 'subject',
                'body', 'sent_at', 'read_at', 'replied_at', 'sender_deleted_at',
                'recipient_deleted_at')


class EloueMessageAdmin(MessageAdmin):
    form = EloueMessageAdminForm

    list_filter = ('sent_at',)
    search_fields = ('subject', 'body', 'recipient__username', 'sender__username', 'recipient__email', 'sender__email',)
    readonly_fields = ('recipient', 'sender', 'parent_msg','sender_profil_link', 'recipient_profil_link',)


    fieldsets = (
        (None, {
            'fields': (
                ('sender', 'sender_profil_link'),
                ('recipient', 'recipient_profil_link', 'group'),
            ),
        }),
        (_('Message'), {
            'fields': (
                'parent_msg',
                'subject', 'body',
            ),
            'classes': ('monospace' ),
        }),
        (_('Date/time'), {
            'fields': (
                'sent_at', 'read_at', 'replied_at',
                'sender_deleted_at', 'recipient_deleted_at',
            ),
            'classes': ('collapse', 'wide'),
        }),
    )

    def sender_profil_link(self, obj):
        sender = obj.sender
        sender_profil_link = '<a href="/edit/accounts/patron/%s" target="_blank">Lien vers la page de l\'expediteur</a>' % sender.pk
        return _(sender_profil_link) 
    sender_profil_link.allow_tags = True
    sender_profil_link.short_description = _(u" ")

    def recipient_profil_link(self, obj):
        recipient_profil_link = '<a href="/edit/accounts/patron/%s" target="_blank">Lien vers la page du destinataire</a>' % obj.recipient.pk
        return _(recipient_profil_link) 
    recipient_profil_link.allow_tags = True
    recipient_profil_link.short_description = _(u" ")

try:
    admin.site.register(Product, ProductAdmin)
    admin.site.register(CarProduct, CarProductAdmin)
    admin.site.register(RealEstateProduct, RealEstateProductAdmin)
    admin.site.register(Category, CategoryAdmin)
    admin.site.register(Property, PropertyAdmin)
    admin.site.register(Curiosity, CuriosityAdmin)
    admin.site.register(ProductReview, ProductReviewAdmin)
    admin.site.register(PatronReview, PatronReviewAdmin)
    admin.site.register(Alert, AlertAdmin)
    admin.site.unregister(Message)
    admin.site.register(Message, EloueMessageAdmin)
except admin.sites.AlreadyRegistered, e:
    log.warn('Site is already registered : %s' % e)
