# coding=utf-8
from django.core.management.base import BaseCommand
from products.models import Product


class Command(BaseCommand):

    def handle(self, *args, **options):
        for product in Product.on_site.all():
            product.save()
