# coding=utf-8
from django.core.management.base import BaseCommand
from django.db import transaction
from products.models import Category, Product
from rent.models import Booking


class Command(BaseCommand):

    @transaction.atomic
    def handle(self, *args, **options):
        gosport_site_id = 13

        print u'Delete duplicates...'
        for slug in ['sports-dhiver-et-de-glace']:
            categories = Category.on_site.filter(slug=slug)
            correct_category = categories[0]
            wrong_categories = categories[1:]

            for category in Category.objects.filter(parent__in=wrong_categories):
                category.parent = correct_category
                category.save()
                category.sites.clear()
                category.sites.add(gosport_site_id)

            for product in Product.objects.filter(category__in=wrong_categories):
                product.category = correct_category
                product.save()

            for category in wrong_categories:
                for product in Product.objects.filter(categories=category):
                    product.categories.remove(category)
                    product.categories.add(correct_category)
                    product.save()

            for category in wrong_categories:
                category.delete()

        print u'Delete categories...'
        category_ids = [176, 181, 251, 585, 247]
        for category in Category.objects.filter(pk__in=category_ids):
            category.sites.remove(gosport_site_id)
            for descendant in Category.objects.filter(tree_id=category.tree_id, lft__gt=category.lft, rght__lt=category.rght):
                descendant.sites.remove(gosport_site_id)

        products_to_remove = Product.objects.filter(
            sites__id=gosport_site_id
        ).filter(categories__isnull=True).distinct()
        print u'\tTo delete: %d products' % products_to_remove.count()

        bookings_to_remove = Booking.objects.filter(product__in=products_to_remove)
        print u'\tTo delete: %d bookings' % bookings_to_remove.count()

        print u'Deleting...'

        print u'\tProducts...'
        total = products_to_remove.count()
        for i, product in enumerate(products_to_remove):
            product.save()
            product.sites.remove(gosport_site_id)
            print(u'\r\t\t%d of %d' % (i + 1, total))

        print u'\tBookings...'
        total = bookings_to_remove.count()
        for i, booking in enumerate(bookings_to_remove):
            booking.save()
            booking.sites.remove(gosport_site_id)
            print(u'\r\t\t%d of %d' % (i + 1, total))

        print u'Finished'
