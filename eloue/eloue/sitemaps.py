# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.contrib.flatpages.models import FlatPage

from accounts.models import Patron
from products.models import Product, Category

USE_HTTPS = getattr(settings, 'USE_HTTPS', True)


class SecureSitemap(Sitemap):
    def get_urls(self, *args, **kwargs):
        if USE_HTTPS:
            kwargs['protocol'] = 'https'
        return super(SecureSitemap, self).get_urls(*args, **kwargs)
    

class PatronSitemap(SecureSitemap):
    changefreq = "weekly"
    limit=1000
    
    def items(self):
        return Patron.on_site.all()
    
    def lastmod(self, patron):
        return patron.modified_at

class ProductSitemap(SecureSitemap):
    changefreq = "weekly"
    limit = 1000

    def items(self):
        return Product.on_site.active()
    
    def lastmod(self, product):
        return product.modified_at

class FlatPageSitemap(SecureSitemap):
    changefreq = "monthly"
    
    def items(self):
        return FlatPage.objects.all()
    

class CategorySitemap(SecureSitemap):
    changefreq = "daily"
    
    def items(self):
        return Category.on_site.all()
    
