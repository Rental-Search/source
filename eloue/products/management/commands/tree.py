import yaml
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    def handle(self, *args, **options):
        from eloue.products.models import Category
        data = yaml.load(open('/home/e-loue/Projets/eloue/eloue/products/management/commands/fixtures/categories.yaml'))
        for section in data:
            root = Category.objects.create(name=section)
            for sub_section in data[section]:
                parent = Category.objects.create(name=sub_section, parent=root)
                for cat in data[section][sub_section]:
                    category = Category.objects.create(name=cat, parent=parent)

