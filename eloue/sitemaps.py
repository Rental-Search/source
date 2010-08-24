# -*- coding: utf-8 -*-
from django.contrib.sitemaps import Sitemap
from django.contrib.flatpages.models import FlatPage

from eloue.accounts.models import Patron
from eloue.products.models import Product

class PatronSitemap(Sitemap):
    changefreq = "weekly"
    
    def items(self):
        return Patron.objects.all()
    

class ProductSitemap(Sitemap):
    changefreq = "weekly"
    
    def items(self):
        return Product.objects.active()
    

class FlatPageSitemap(Sitemap):
	changefreq = "monthly"

	def items(self):
		return FlatPage.objects.all()
    
