# coding=utf-8
from django.core.management.base import BaseCommand
from django.utils.translation.trans_real import translation
from products.models import Category, Product
from rent.models import Booking


class Command(BaseCommand):
    help = "Make existing products with proper category to be available on GoSport."

    def handle(self, *args, **options):
        eloue_site_id = 1
        gosport_site_id = 13

        print u'Import categories...'
        category_ids = [176, 181, 251, 585, 247]
        for category in Category.objects.filter(pk__in=category_ids):
            category.sites.add(gosport_site_id)
            for descendant in Category.objects.filter(tree_id=category.tree_id, lft__gt=category.lft, rght__lt=category.rght):
                descendant.sites.add(gosport_site_id)

        categories = Category.objects.filter(sites__id=gosport_site_id).all()
        print u'\tCategories found: %d' % categories.count()

        if categories.exists():
            print u'Search products'
            gosport_products = Product.objects.filter(sites__id=gosport_site_id).all()
            eloue_products = Product.objects.filter(sites__id=eloue_site_id).all()
            products_to_import = eloue_products.filter(
                category__in=categories
            ).exclude(pk__in=gosport_products)
            products_to_delete = gosport_products.exclude(category__in=categories)
            print u'\tTo import: %d products' % products_to_import.count()
            print u'\tTo delete: %d products' % products_to_delete.count()

            print u'Search bookings'
            gosport_bookings = Booking.objects.filter(sites__id=gosport_site_id).all()
            eloue_bookings = Booking.objects.filter(sites__id=eloue_site_id).all()
            bookings_to_import = eloue_bookings.filter(
                product__category__in=categories
            ).exclude(pk__in=gosport_bookings)
            bookings_to_delete = gosport_bookings.exclude(product__category__in=categories)
            print u'\tTo import: %d bookings' % bookings_to_import.count()
            print u'\tTo delete: %d bookings' % bookings_to_delete.count()

            print u'Importing...'

            print u'\tProducts...'
            total = products_to_import.count()
            for i, product in enumerate(products_to_import):
                product.sites.add(gosport_site_id)
                product.save()
                print(u'\r\t\t%d of %d' % (i + 1, total))

            print u'\tBookings...'
            total = bookings_to_import.count()
            for i, booking in enumerate(bookings_to_import):
                booking.sites.add(gosport_site_id)
                booking.save()
                print(u'\r\t\t%d of %d' % (i + 1, total))

            print u'Deleting...'

            print u'\tProducts...'
            total = products_to_delete.count()
            for i, product in enumerate(products_to_delete):
                product.sites.remove(gosport_site_id)
                product.save()
                print(u'\r\t\t%d of %d' % (i + 1, total))

            print u'\tBookings...'
            total = bookings_to_delete.count()
            for i, booking in enumerate(bookings_to_delete):
                booking.sites.remove(gosport_site_id)
                booking.save()
                print(u'\r\t\t%d of %d' % (i + 1, total))

        print u'Finished'
