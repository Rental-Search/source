# -*- coding: utf-8 -*-
from django.contrib import admin

from eloue.products.models import Product, Picture, Category, Property, PropertyValue, Price, ProductReview, PatronReview

from haystack.admin import SearchModelAdmin

class PictureInline(admin.TabularInline):
    model = Picture

class PropertyValueInline(admin.TabularInline):
    model = PropertyValue

class PriceInline(admin.TabularInline):
    model = Price

class ProductAdmin(SearchModelAdmin):
    search_fields = ['summary', 'description']
    inlines = [ PictureInline, PropertyValueInline, PriceInline ]
    raw_id_fields = ("owner", "address")
    list_display = ('summary', 'deposit', 'quantity', 'is_archived', 'is_allowed')
    list_filter = ('is_archived', 'is_allowed')

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ['name', 'parent__name']

class PropertyAdmin(admin.ModelAdmin):
    pass

class ProductReviewAdmin(admin.ModelAdmin):
    raw_id_fields = ("reviewer", "product")


class PatronReviewAdmin(admin.ModelAdmin):
    raw_id_fields = ("reviewer", "patron")


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Property, PropertyAdmin)
admin.site.register(ProductReview, ProductReviewAdmin)
admin.site.register(PatronReview, PatronReviewAdmin)
