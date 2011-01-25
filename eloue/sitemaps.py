# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.contrib.flatpages.models import FlatPage

from eloue.accounts.models import Patron
from eloue.products.models import Product, Category

USE_HTTPS = getattr(settings, 'USE_HTTPS', True)


class SecureSitemap(Sitemap):
    def get_urls(self, page=1, site=None):
        urls = super(SecureSitemap, self).get_urls(page, site)
        if USE_HTTPS:
            for url in urls:
                url['location'] = url['location'].replace("http://", 'https://')
        return urls
    

class PatronSitemap(SecureSitemap):
    changefreq = "weekly"
    
    def items(self):
        return Patron.on_site.all()
    

class ProductSitemap(SecureSitemap):
    changefreq = "weekly"
    
    def items(self):
        return Product.on_site.active()
    

class FlatPageSitemap(SecureSitemap):
    changefreq = "monthly"
    
    def items(self):
        return FlatPage.objects.all()
    

class CategorySitemap(SecureSitemap):
    changefreq = "daily"
    
    def items(self):
        return Category.objects.all()
    
