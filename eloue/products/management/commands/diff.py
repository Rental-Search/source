# -*- coding: utf-8 -*-
import os
import yaml
from optparse import make_option

from django.core.management.base import BaseCommand

local_path = lambda path: os.path.join(os.path.dirname(__file__), path)

class Command(BaseCommand):
    help = "Dump or load categories changes"
    option_list = BaseCommand.option_list + (
        make_option('--load',
            action='store_true',
            dest='load',
            default=False,
            help='Load differences'
        ),
        make_option('--dump',
            action='store_true',
            dest='dump',
            default=False,
            help='Dump differences'
        )
    )
    
    def handle(self, *args, **options):
        if options.get('load'):
            self.load()
        elif options.get('dump'):
            self.dump()
    
    def load(self):
        from eloue.products.models import Product
        data = yaml.load(open(local_path('fixtures/differences.yaml'), 'r'))
        for diff in data:
            Product.objects.filter(pk=diff['pk']).update(category=diff['category'])
    
    def dump(self):
        from eloue.products.models import Product
        data = []
        for product in Product.objects.iterator():
            data.append({
                'pk':product.pk,
                'category':product.category.pk
            })
        yaml.dump(data, open(local_path('fixtures/differences.yaml'), 'w'))
    
