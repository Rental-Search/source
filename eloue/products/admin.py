# -*- coding: utf-8 -*-
import decimal

from django.contrib import admin, messages
from django.shortcuts import redirect

from mptt.admin import MPTTModelAdmin
from mptt.forms import TreeNodeChoiceField

from eloue.admin import CurrentSiteAdmin
from eloue.products.forms import ProductAdminForm

from eloue.products.models import Alert, Product, CarProduct, RealEstateProduct, Picture, Category, Property, PropertyValue, Price, ProductReview, PatronReview, Curiosity, ProductRelatedMessage, CategoryDescription


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

class ProductAdmin(CurrentSiteAdmin):
    date_hierarchy = 'created_at'
    search_fields = ['summary', 'description', 'category__name', 'owner__username', 'owner__email']
    inlines = [PictureInline, PropertyValueInline, PriceInline]
    raw_id_fields = ("owner", "address")
    list_display = ('summary', 'category', 'deposit_amount', 'quantity', 'is_archived', 'is_allowed', 'created_at')
    list_filter = ('is_archived', 'is_allowed', 'category')
    list_editable = ('category',)
    ordering = ['-created_at']
    list_per_page = 20
    form = ProductAdminForm
    actions = [convert_to_carproduct, convert_to_realestateproduct]  
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'category':
            kwargs['form_class'] = TreeNodeChoiceField
            kwargs['empty_label'] = u"Choisissez une catégorie"
            kwargs['level_indicator'] = u"--"
            kwargs['queryset'] = Category.tree.all()
        return super(ProductAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    
    def queryset(self, request):
        qs = super(ProductAdmin, self).queryset(request)
        return qs.filter(carproduct=None, realestateproduct=None)

class RealEstateProductAdmin(CurrentSiteAdmin):
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'category':
            kwargs['form_class'] = TreeNodeChoiceField
            kwargs['empty_label'] = u"Choisissez une catégorie"
            kwargs['level_indicator'] = u"--"
            kwargs['queryset'] = Category.tree.get(name=u'Location saisonnière').get_descendants()
        return super(RealEstateProductAdmin, self).formfield_for_dbfield(db_field, **kwargs)

class CarProductAdmin(CurrentSiteAdmin):
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'category':
            kwargs['form_class'] = TreeNodeChoiceField
            kwargs['empty_label'] = u"Choisissez une catégorie"
            kwargs['level_indicator'] = u"--"
            kwargs['queryset'] = Category.tree.get(name=u'Automobile').get_descendants()
        return super(CarProductAdmin, self).formfield_for_dbfield(db_field, **kwargs)

class CategoryDescriptionInline(admin.StackedInline):
    model = CategoryDescription

class CategoryAdmin(MPTTModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ['name', 'parent__name']
    prepopulated_fields = {"slug": ("name",)}
    inlines = [CategoryDescriptionInline]


class PropertyAdmin(admin.ModelAdmin):
    pass


class ProductReviewAdmin(admin.ModelAdmin):
    raw_id_fields = ("reviewer", "product")


class PatronReviewAdmin(admin.ModelAdmin):
    raw_id_fields = ("reviewer", "patron")


class CuriosityAdmin(CurrentSiteAdmin):
    list_display = ('product',)
    raw_id_fields = ("product",)

#class ProductRelatedMessageAdmin(admin.ModelAdmin):
#    list_display = ('product',)
#    raw_id_fields = ("product",)

class AlertAdmin(admin.ModelAdmin):
    pass


admin.site.register(Product, ProductAdmin)
admin.site.register(CarProduct, CarProductAdmin)
admin.site.register(RealEstateProduct, RealEstateProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Property, PropertyAdmin)
admin.site.register(Curiosity, CuriosityAdmin)
admin.site.register(ProductReview, ProductReviewAdmin)
admin.site.register(PatronReview, PatronReviewAdmin)
#admin.site.register(ProductRelatedMessage, ProductRelatedMessageAdmin)
admin.site.register(Alert, AlertAdmin)
