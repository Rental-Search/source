# -*- coding: utf-8 -*-
from django.contrib import admin

from mptt.admin import MPTTModelAdmin
from mptt.forms import TreeNodeChoiceField

from eloue.admin import CurrentSiteAdmin
from eloue.products.forms import ProductAdminForm
from eloue.products.models import Product, Picture, Category, Property, PropertyValue, Price, ProductReview, PatronReview, Curiosity, ProductRelatedMessage


class PictureInline(admin.TabularInline):
    model = Picture


class PropertyValueInline(admin.TabularInline):
    model = PropertyValue


class PriceInline(admin.TabularInline):
    model = Price


class ProductAdmin(CurrentSiteAdmin):
    date_hierarchy = 'created_at'
    search_fields = ['summary', 'description', 'category__name', 'owner__username', 'owner__email']
    inlines = [PictureInline, PropertyValueInline, PriceInline]
    raw_id_fields = ("owner", "address")
    list_display = ('summary', 'category', 'deposit_amount', 'quantity', 'is_archived', 'is_allowed', 'created_at')
    list_filter = ('is_archived', 'is_allowed')
    list_editable = ('category',)
    ordering = ['-created_at']
    list_per_page = 20
    form = ProductAdminForm
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'category':
            kwargs['form_class'] = TreeNodeChoiceField
            kwargs['empty_label'] = u"Choisissez une catégorie"
            kwargs['level_indicator'] = u"--"
            kwargs['queryset'] = Category.tree.all()
        return super(ProductAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    

class CategoryAdmin(MPTTModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ['name', 'parent__name']
    prepopulated_fields = {"slug": ("name",)}


class PropertyAdmin(admin.ModelAdmin):
    pass


class ProductReviewAdmin(admin.ModelAdmin):
    raw_id_fields = ("reviewer", "product")


class PatronReviewAdmin(admin.ModelAdmin):
    raw_id_fields = ("reviewer", "patron")


class CuriosityAdmin(CurrentSiteAdmin):
    list_display = ('product',)
    raw_id_fields = ("product",)

class ProductRelatedMessageAdmin(admin.ModelAdmin):
    list_display = ('product',)
    raw_id_fields = ("product",)

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Property, PropertyAdmin)
admin.site.register(Curiosity, CuriosityAdmin)
admin.site.register(ProductReview, ProductReviewAdmin)
admin.site.register(PatronReview, PatronReviewAdmin)
admin.site.register(ProductRelatedMessage, ProductRelatedMessageAdmin)




