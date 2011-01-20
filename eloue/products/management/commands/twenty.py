# -*- coding: utf-8 -*-
import httplib2
import logbook
import os
import re
import urlparse

from django.core.management.base import BaseCommand
from django.utils.encoding import smart_unicode

from eloue.utils import generate_camo_url

log = logbook.Logger('eloue.rent.twenty')


class Command(BaseCommand):
    help = "Update footer and header template"
    
    def handle(self, *args, **options):
        from django.conf import settings
        log.info('Starting downloading footer and header')
        try:
            http = httplib2.Http()
            
            # Downloading header
            response, content = http.request("http://www.20minutes.fr/api/v1/layout/header?partner=eloue")
            content = smart_unicode(content, encoding='latin1')
            content = content.replace("<!-- {{PARTNER_ASSETS}} -->", "{% load compressed %}{% block head %}{% compressed_css 'twenty' %}{% endblock %}")
            content = content.replace("<title>20minutes.fr</title>", "<title>Tout louer en ligne avec 20minutes.fr et e-loue.com</title>")
            content = content.replace("""<div class="mn-doc">""", """{% if messages %}{% for message in messages %}<div id="notification" class="notification {% if message.tags %} {{ message.tags }}"{% endif %}><span id="notification-text">{{ message }}</span></div>{% endfor %}{% endif %}<div class="mn-doc">""")
            content = content.replace("//GA_VARS//", """_gaq.push(['e._setAccount', 'UA-8258979-3']); _gaq.push(['e._setDomainName', 'e-loue.20minutes.fr']); _gaq.push(['e._trackPageview']);""")
            for match in re.finditer(r'[\"\'](http://cache.20minutes.fr/.*)[\"\']', content):
                original_url = match.group(1)
                if not original_url.endswith('.js'):
                    camo_url = generate_camo_url(original_url)
                    content = content.replace(original_url, camo_url)
                else:
                    parts = urlparse.urlparse(original_url)
                    content = content.replace(original_url, "https://media.e-loue.com/20mn%s" % parts.path)
            header = open(os.path.join(settings.TEMPLATE_DIRS[0], 'header.html'), 'w')
            header.write(content.encode('utf-8'))
            header.close()
            
            # Downloading footer
            response, content = http.request("http://www.20minutes.fr/api/v1/layout/footer?partner=eloue")
            content = smart_unicode(content, encoding='latin1')
            content = content.replace("<!-- {{PARTNER_ASSETS}} -->", "{% load compressed %}{% block tail %}{% compressed_js 'application' %}{% endblock %}")
            for match in re.finditer(r'[\"\'](http://cache.20minutes.fr/.*)[\"\']', content):
                original_url = match.group(1)
                if not original_url.endswith('.js'):
                    camo_url = generate_camo_url(original_url)
                    content = content.replace(original_url, camo_url)
                else:
                    parts = urlparse.urlparse(original_url)
                    content = content.replace(original_url, "https://media.e-loue.com/20mn%s" % parts.path)
            footer = open(os.path.join(settings.TEMPLATE_DIRS[0], 'footer.html'), 'w')
            footer.write(content.encode('utf-8'))
            footer.close()
        except (httplib2.HttpLib2Error, IOError), e:
            log.exception("Downloading footer and header failed")
        log.info('Starting downloading footer and header')
    
