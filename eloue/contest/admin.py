from django.contrib import admin
from django.core.urlresolvers import reverse

from contest.models import Gamer, ProductGamer


class ProductGamerInline(admin.TabularInline):
	model = ProductGamer
	readonly_fields = ('product_url', 'created_at')
	exclude = ('product',)
	ordering = ['-created_at']

	def product_url(self, obj):
		try:
			obj.product.carproduct
			return '<a href="%(link)s">%(product)s</a>' % {'product': obj.product, 'link': reverse('admin:products_carproduct_change', args=[obj.product.pk])}
		except:
			pass
		try:
			obj.product.realestateproduct
			return '<a href="%(link)s">%(product)s</a>' % {'product': obj.product, 'link': reverse('admin:products_realestateproduct_change', args=[obj.product.pk])}
		except:
			pass
		return '<a href="%(link)s">%(product)s</a>' % {'product': obj.product, 'link': reverse('admin:products_product_change', args=[obj.product.pk])}
	product_url.allow_tags = True


class ProductGamerAdmin(admin.ModelAdmin):
	readonly_fields = ('product_url', 'gamer_url', 'created_at')
	exclude = ('product', 'gamer')
	ordering = ['-created_at']
	list_display = ['gamer', 'product', 'created_at']
	date_hierarchy = 'created_at'

	def product_url(self, obj):
		try:
			obj.product.carproduct
			return '<a href="%(link)s">%(product)s</a>' % {'product': obj.product, 'link': reverse('admin:products_carproduct_change', args=[obj.product.pk])}
		except:
			pass
		try:
			obj.product.realestateproduct
			return '<a href="%(link)s">%(product)s</a>' % {'product': obj.product, 'link': reverse('admin:products_realestateproduct_change', args=[obj.product.pk])}
		except:
			pass
		return '<a href="%(link)s">%(product)s</a>' % {'product': obj.product, 'link': reverse('admin:products_product_change', args=[obj.product.pk])}
	product_url.allow_tags = True

	def gamer_url(self, obj):
		return '<a href="%(link)s">%(gamer)s</a>' % {'gamer': obj.gamer, 'link': reverse('admin:contest_gamer_change', args=[obj.gamer.pk])}
	gamer_url.allow_tags = True

class GamerAdmin(admin.ModelAdmin):
	inlines = [ProductGamerInline, ]
	readonly_fields = ('patron', 'like_facebook', 'created_at')
	exclude = ('birthday', )
	list_display = ('patron', 'like_facebook', 'created_at')
	ordering = ['-created_at']
	date_hierarchy = 'created_at'



admin.site.register(Gamer, GamerAdmin)
admin.site.register(ProductGamer, ProductGamerAdmin)