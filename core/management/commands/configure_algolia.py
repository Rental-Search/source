from django.core.management.base import BaseCommand
from eloue import settings
from algoliasearch import algoliasearch


class Command(BaseCommand):
    
    help =\
'''Configures all indices from the ALGOLIA_INDICES setting'''
    
    def handle(self, *args, **options):
        
        conn_settings = settings.HAYSTACK_CONNECTIONS['default']
        app_id = conn_settings['APP_ID']
        app_key = conn_settings['API_KEY']
        prefix = conn_settings['INDEX_NAME_PREFIX']
        
        c = algoliasearch.Client(app_id, app_key)
        
        masters = settings.ALGOLIA_INDICES
        
        self.stdout.write("Configuring:")
        for m_name, m_sett in masters.items():
            slaves = m_sett['slaves']
            m_copy = m_sett.copy()
            del m_copy['slaves']
            m_full_name = prefix + m_name
            self.stdout.write(' '+m_full_name)
            master = c.init_index(m_full_name)
            s_full_names = []
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

        