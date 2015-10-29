# coding=utf-8
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.db import transaction
from products.models import Category, Product, CategoryConformity
from rent.models import Booking

class Command(BaseCommand):

	categories_tree = [
		{
			'name': u'Femme',
			'children': [
				{
					'name': u'Robes',
					'new_children': [
						u'Robes de coktails',
						u'Robes longues',
						u'Robes orientales',
						u'Robes de luxe',
						u'Robes de mariage',
						u'Robes de maternité'
					]
				},
				{
					'name': u'Accessoires femme',
					'new_children': [
						u'Pochettes',
						u'Bijoux',
						u'Chapeaux & Accessoire de tête',
						u'Etoles',
						u'Manteaux & vestes',
					]
				},
				{
					'name': u'Chaussures femme',
					'new_children': [
						u'Escarpins classiques',
						u'Escarpins à bout ouvert',
						u'Chaussures de marié',
						u'Talonts hauts',
						u'Composés à plateformes',
						u'Ballerines'
					]
				},
			],
		},
		{
			'name': u'Homme',
			'children': [
				{
					'name': u'Costumes & Smokings',
					'new_children': [
						u'Vestes classiques',
						u'Queue de pie',
						u'Pantalons',
						u'Jaquettes',
					]
				},
				{
					'name': u'Accessoires homme',
					'new_children': [
						u'Gilets',
						u'Lavalières',
						u'Chapeaux',
						u'Cravates',
						u'Nœuds papillons',
						u'Boutons de manchettes'
					]
				},
				{
					'name': u'Chaussures homme',
					'new_children': [
						u'Mocassins',
						u'derbie, richelieu',
						u'Boots, chaussures montantes',
					]
				},
			],
		},
		{
			'name': u'Enfants',
			'children': [
				{
					'name': u'Fille',
					'new_children': [
						u'Robe et cotèges',
						u'Chaussures fille',
						u'Accessoires fille',
					]
				},
				{
					'name': u'Garçon',
					'new_children': [
						u'Costumes et Smokings',
						u'Chaussures garçon',
						u'Accessoires garçon',
					]
				},
			],
		},
	]

	@transaction.atomic
	def handle(self, *args, **options):
		assert Site.objects.get_current().pk == 15
		dressbooking_site_id = 15
		eloue_site_id = 1

		def create_category(description, parent_category=None):
			category = Category.objects.create(
				name=description['name'],
				parent=parent_category
			)
			category.sites.clear()
			category.sites.add(dressbooking_site_id)

			for eloue_category in description.get('from', []):
				CategoryConformity.objects.create(
					eloue_category_id=eloue_category,
					gosport_category=category)

			for child_category_name in description.get('new_children', []):
				child_category = Category.objects.create(
					name=child_category_name,
					parent=category
				)
				child_category.sites.clear()
				child_category.sites.add(dressbooking_site_id)

			for child_category_description in description.get('children', []):
				create_category(child_category_description, category)

		for new_categories in self.categories_tree:
			create_category(new_categories)
		gosport_categories = Category.objects.filter(sites__id=dressbooking_site_id).all()

		for gosport_category in gosport_categories:
			for conformity in CategoryConformity.objects.filter(gosport_category=gosport_category):
				products_to_import = Product.objects.filter(sites__id=eloue_site_id, category=conformity.eloue_category)
				bookings_to_import = Booking.objects.filter(product__in=products_to_import)

				for product in products_to_import:
					product.sites.add(dressbooking_site_id)

				for booking in bookings_to_import:
					booking.sites.add(dressbooking_site_id)