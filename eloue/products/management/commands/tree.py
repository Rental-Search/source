# -*- coding: utf-8 -*-
import yaml

from django.core.management.base import BaseCommand, CommandError

local_path = lambda path: os.path.join(os.path.dirname(__file__), path)

class Command(BaseCommand):
    def handle(self, *args, **options):
        from eloue.products.models import Category
        data = yaml.load(open(local_path('fixtures/categories.yaml'))
        for section in data:
            root = Category.objects.create(name=section)
            for sub_section in data[section]:
                parent = Category.objects.create(name=sub_section, parent=root)
                for cat in data[section][sub_section]:
                    category = Category.objects.create(name=cat, parent=parent)

