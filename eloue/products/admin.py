# -*- coding: utf-8 -*-
from django.contrib import admin

from eloue.products.models import Product, Picture, Category, Property, PropertyValue, SeasonalPrice, StandardPrice, Review

class PictureInline(admin.TabularInline):
    model = Picture

class PropertyValueInline(admin.TabularInline):
    model = PropertyValue

class SeasonalPriceInline(admin.TabularInline):
    model = SeasonalPrice

class StandardPriceInline(admin.TabularInline):
    model = StandardPrice

class ProductAdmin(admin.ModelAdmin):
    search_fields = ['summary', 'description']
    inlines = [ PictureInline, PropertyValueInline, StandardPriceInline, SeasonalPriceInline ]
    raw_id_fields = ("owner", "address")
    list_display = ('summary', 'deposit', 'quantity', 'is_archived', 'is_allowed')
    list_filter = ('is_archived', 'is_allowed')

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ['name', 'parent__name']

class PropertyAdmin(admin.ModelAdmin):
    pass

class ReviewAdmin(admin.ModelAdmin):
    pass

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Property, PropertyAdmin)
admin.site.register(Review, ReviewAdmin)