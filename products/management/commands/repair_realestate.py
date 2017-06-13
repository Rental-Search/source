# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.db import connection

from products.models import Product, Category, RealEstateProduct


class Command(BaseCommand):
    help = 'Repaire RealEstateProducts what do not have entries into products_realestateproduct table'

    def handle(self, *args, **options):
        # RealEstate root category
        root_category = Category.objects.get(id=2713)
        category_ids = [x.id for x in root_category.get_descendants(include_self=True)]

        # Retrive realestate products without entry into RealEstateProduct table
        product_ids = Product.objects.filter(
            category__in=category_ids,
            realestateproduct__isnull=True).values_list('id')

        cursor = connection.cursor()
        cursor.executemany("""
                INSERT INTO products_realestateproduct(product_ptr_id, capacity, private_life, chamber_number)
                VALUES(%s, 1, 1, 1)""", product_ids)
        connection.commit()

        # Signals
        for product in RealEstateProduct.objects.filter(id=product_ids):
            product.save()
