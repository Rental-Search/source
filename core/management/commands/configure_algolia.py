from django.core.management.base import BaseCommand
from eloue import settings
from algoliasearch import algoliasearch
from copy import deepcopy
from products.models import Property
from optparse import make_option


class Command(BaseCommand):
    
    help =\
'''
Configures all indices from the ALGOLIA_INDICES setting.
'''
    option_list = BaseCommand.option_list + (
        make_option('--with-property-facets',
            action='store_true',
            dest='property_facets',
            default=False,
            help='Add all attribute names that can appear "+\
                "in indexed objects to product index facets'),
        )
    
    def handle(self, *args, **options):
        
        conn_settings = settings.HAYSTACK_CONNECTIONS['algolia']
        app_id = conn_settings['APP_ID']
        app_key = conn_settings['API_KEY']
        prefix = conn_settings['INDEX_NAME_PREFIX']
        
        c = algoliasearch.Client(app_id, app_key)
        
        masters = deepcopy(settings.ALGOLIA_INDICES)
        
        if options['property_facets']:
            # FIXME add generic attributes when there are many properties
            # Add all attribute names that can appear in indexed objects
            property_facets = Property.get_attr_names()
            self.stdout.write('Adding {} property facets'.format(len(property_facets)))
            masters['products.product']['attributesForFaceting']\
                    .extend(property_facets)
        
        self.stdout.write("Configuring:")
        for m_name, m_sett in masters.items():
            slaves = m_sett.get('slaves')
            m_copy = m_sett.copy()
            m_full_name = prefix + m_name
            self.stdout.write(' '+m_full_name)
            master = c.init_index(m_full_name)
            s_full_names = []
            if slaves:
                del m_copy['slaves']
                for suffix, s_sett in slaves.items():
                    s_full_name = m_full_name + '_' + suffix
                    s_full_names.append(s_full_name)
                    self.stdout.write('  '+s_full_name)
                    slave = c.init_index(s_full_name)
                    s_copy = m_copy.copy()
                    s_copy.update(s_sett)
                    slave.set_settings(s_copy)
                m_copy['slaves'] = s_full_names
            master.set_settings(m_copy)
        
        self.stdout.write('Done.')

        