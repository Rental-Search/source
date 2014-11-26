# coding=utf-8
from django.core.management.base import BaseCommand
from django.db import transaction
from products.models import Category, Product, CategoryConformity
from rent.models import Booking


class Command(BaseCommand):

    new_categories = {
        'name': u'Sports & Loisirs',
        'from': [172, 585, 217, 238, 173, 232, ],
        'children': [
            {
                'name': u'Sports d\'extérieur',
                'children': [
                    {
                        'name': u'Pétanque',
                        'from': [230, ],
                    },
                    {
                        'name': u'Golf',
                        'from': [595, ]
                    },
                    {
                        'name': u'Pêche',
                        'from': [229, ]
                    },
                    {
                        'name': u'Tir à l\'arc',
                        'from': [243, ]
                    },
                    {
                        'name': u'Equitation',
                        'from': [594, ]
                    },
                    {
                        'name': u'Chasse',
                        'from': [592, ]
                    }
                ]
            },
            {
                'name': u'Sports de raquette',
                'children': [
                    {
                        'name': u'Tennis',
                        'from': [241, ],
                    },
                    {
                        'name': u'Badminton',
                        'from': [211, ]
                    },
                    {
                        'name': u'Squash',
                        'from': [2, ]
                    },
                    {
                        'name': u'Tennis de table',
                        'from': [242, ]
                    }
                ]
            },
            {
                'name': u'Cycles',
                'from': [249, ],
                'new_children': [
                    u'Tricycle - Rosalie',
                    # u'Protections',
                    u'Vélo électrique',
                ],
                'children': [
                    {
                        'name': u'VTT et VTC',
                        'from': [590, 247, ]
                    },
                    {
                        'name': u'Accessoires',
                        'from': [689, ]
                    },
                    {
                        'name': u'Vélo de ville',
                        'from': [248, ]
                    },
                    {
                        'name': u'Tandem',
                        'from': [688, ]
                    },
                    {
                        'name': u'BMX',
                        'from': [250, ]
                    }
                ]
            },
            {
                'name': u'Sports mécaniques et aériens',
                'new_children': [
                    u'Karting',
                    u'Quad et Buggy',
                ],
                'children': [
                    {
                        'name': u'Avions - Hélicoptère',
                        'from': [575, 176, 179, 180, 251, 252, 591, ]
                    },
                    {
                        'name': u'Mini Moto',
                        'from': [589, ]
                    },
                    {
                        'name': u'Segway',
                        'from': [245, ]
                    },
                    {
                        'name': u'Mongolfière',
                        'from': [177, ]
                    },
                    {
                        'name': u'ULM - Planeur',
                        'from': [178, 574, ]
                    }
                ]
            },
            {
                'name': u'Sports d\'eau',
                'new_children': [
                    u'Kitesurf',
                    u'Ski nautique',
                    u'Wakeboard - Wakesurf',
                    u'Combinaisons',
                    u'Waterpolo',
                    u'Aquagym',
                ],
                'children': [
                    {
                        'name': u'Bateaux',
                        'from': [185, 207, 197, 584, 192, 189, 734, 187, 182, 183, 191, 194, 186, 580, 184, 188, 190, 193, 576, 577, 578, 579, 581, 181, 206, 195, 205, 203, 204, 196, 198, 199, 200, 201, 202, 582, 583, 735]
                    },
                    {
                        'name': u'Plongée - Snorkeling',
                        'from': [598, ]
                    },
                    {
                        'name': u'Surf',
                        'from': [240, ]
                    },
                    {
                        'name': u'Jet Ski - Scooter des mers',
                        'from': [209, ]
                    },
                    {
                        'name': u'Canoë kayak',
                        'from': [214]
                    },
                    {
                        'name': u'Planche à voile',
                        'from': [231, ]
                    },
                    {
                        'name': u'Bodyboard',
                        'from': [212, ]
                    },
                    {
                        'name': u'Natation',
                        'from': [597, ]
                    },
                    {
                        'name': u'Pédalo',
                        'from': [208, ]
                    },
                    {
                        'name': u'Paddle',
                        'from': [228, ]
                    }
                ]
            },
            {
                'name': u'Loisirs',
                'new_children': [
                    u'Billards',
                    u'Baby Foot',
                    u'Activités manuelles',
                ],
                'children': [
                    {
                        'name': u'Jeux de société',
                        'from': [573, 175, ]
                    },
                    {
                        'name': u'Jeux d\'adresse',
                        'from': [174, 220, ]
                    },
                    {
                        'name': u'Cerfs Volants',
                        'from': [215, ]
                    },
                    {
                        'name': u'Chars à voile',
                        'from': [246, ]
                    }
                ]
            },
            {
                'name': u'Sports d\'hiver et de glace',
                'new_children': [
                    u'Ski de fond',
                    u'Raquette',
                    u'Luge',
                    # u'Protections',
                    u'Patinage artistique',
                ],
                'children': [
                    {
                        'name': u'Ski alpin',
                        'from': [273, ]
                    },
                    {
                        'name': u'Snowboard',
                        'from': [599, ]
                    },
                ]
            },
            {
                'name': u'Fitness, Gym et Danse',
                'new_children': [
                    u'Petit Matériel',
                    u'Rameur',
                    u'Stepper',
                    u'Vélo d\'appartement',
                    u'Vélo élliptique',
                    u'Appareil à abdos',
                ],
                'children': [
                    {
                        'name': u'Banc de musculation',
                        'from': [219, ]
                    },
                    {
                        'name': u'Tapis de course',
                        'from': [593, ]
                    },
                    {
                        'name': u'Danse',
                        'from': [216, 227, ]
                    },
                    {
                        'name': u'Gymnastique',
                        'from': [222, ]
                    }
                ]
            },
            {
                'name': u'Glisse urbaine',
                'new_children': [
                    # u'Protections',
                ],
                'children': [
                    {
                        'name': u'Trottinette',
                        'from': [588, ]
                    },
                    {
                        'name': u'Roller',
                        'from': [234, ]
                    },
                    {
                        'name': u'Skateboard',
                        'from': [236, ]
                    }
                ]
            },
            {
                'name': u'Sports outdoor',
                'new_children': [
                    u'Canyoning',
                    u'Camping',
                ],
                'children': [
                    {
                        'name': u'Randonnée',
                        'from': [226, ]
                    },
                    {
                        'name': u'Escalade - Spéléologie',
                        'from': [218, ]
                    },
                    {
                        'name': u'Alpinisme',
                        'from': [210, ]
                    }
                ]
            },
            {
                'name': u'Sports d\'équipe',
                'new_children': [
                    u'Hockey sur glace',
                    # u'Protections',
                ],
                'children': [
                    {
                        'name': u'Football - Foot en salle',
                        'from': [221, ]
                    },
                    {
                        'name': u'Football américain',
                        'from': [239, ]
                    },
                    {
                        'name': u'Handball',
                        'from': [223, ]
                    },
                    {
                        'name': u'Rugby',
                        'from': [235, ]
                    },
                    {
                        'name': u'Volleyball',
                        'from': [244, ]
                    },
                    {
                        'name': u'Basketball',
                        'from': [586, ]
                    },
                ]
            },
            {
                'name': u'Sports de combat',
                'new_children': [
                    # u'Protections',
                ],
                'children': [
                    {
                        'name': u'Boxe',
                        'from': [213, ]
                    },
                    {
                        'name': u'Karaté - Kungfu - Taekwondo',
                        'from': [225, 587, 596, ]
                    },
                    {
                        'name': u'Judo',
                        'from': [224, ]
                    }
                ]
            }
        ]
    }

    @transaction.atomic
    def handle(self, *args, **options):
        gosport_site_id = 13
        eloue_site_id = 1

        def create_category(description, parent_category=None):
            category = Category.objects.create(
                name=description['name'],
                parent=parent_category
            )
            category.sites.clear()
            category.sites.add(gosport_site_id)

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
                child_category.sites.add(gosport_site_id)

            for child_category_description in description.get('children', []):
                create_category(child_category_description, category)

        create_category(self.new_categories)
        gosport_categories = Category.objects.filter(sites__id=gosport_site_id).all()

        for gosport_category in gosport_categories:
            for conformity in CategoryConformity.objects.filter(gosport_category=gosport_category):
                products_to_import = Product.objects.filter(sites__id=eloue_site_id, category=conformity.eloue_category)
                bookings_to_import = Booking.objects.filter(product__in=products_to_import)

                for product in products_to_import:
                    product.sites.add(gosport_site_id)

                for booking in bookings_to_import:
                    booking.sites.add(gosport_site_id)
