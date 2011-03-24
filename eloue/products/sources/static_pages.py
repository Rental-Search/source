# -*- coding: utf-8 -*-
import re

from datetime import datetime, timedelta
from httplib2 import Http
from lxml import objectify
from urllib import urlencode

from django.utils.encoding import smart_str

from . import BaseSource, StaticPage
from wordpress import WordPress

URL = 'http://localhost:8888/'

class SourceClass(BaseSource):
    
    def request(self, url):
        wp = WordPress(url)
        return wp.get_recent_posts()
    
    def get_docs(self):
        """
        The format of the return is as follows:
        
        [{'author': u'admin',
          'categories': u'avion',
          'categories_exact': u'avion',
          'django_ct': 'wordpress.staticpage',
          'modified': u'2011-03-24 07:55:13',
          'search_created_at': datetime.datetime(2011, 3, 24, 11, 48, 44, 580441),
          'sites': 'http://localhost:8888/',
          'title': u'test wordpress',
          'title_exact': u'test wordpress',
          'url': u'http://localhost:8888/?p=5',
          'url_link_exact': u'http://localhost:8888/?p=5'},
         {'author': u'admin',
          'categories': u'voiture',
          'categories_exact': u'voiture',
          'django_ct': 'wordpress.staticpage',
          'modified': u'2011-03-24 07:38:11',
          'search_created_at': datetime.datetime(2011, 3, 24, 11, 48, 44, 580458),
          'sites': 'http://localhost:8888/',
          'title': u'Hello world!',
          'title_exact': u'Hello world!',
          'url': u'http://localhost:8888/?p=1',
          'url_link_exact': u'http://localhost:8888/?p=1'}]
        
        """
        docs = []
        response = self.request(URL)
        if response["status"] == "ok":
            for i in range(response["count_total"]):
                unit_post = response["posts"][i]
                docs.append(StaticPage({
                'author': unit_post['author']['nickname'],
                'modified': unit_post['modified'],
                'title': unit_post['title'],
                'categories': unit_post['categories'][0]['title'],
                'url': unit_post['url']
                }))
        return docs
                

