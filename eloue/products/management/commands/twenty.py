# -*- coding: utf-8 -*-
import httplib2
import logbook
import os

from django.core.management.base import BaseCommand
from django.utils.encoding import smart_unicode

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
            content = content.replace("<title>20minutes.fr</title>", "<title>{% block title %}20minutes.fr{% block%}</title>")
            header = open(os.path.join(settings.TEMPLATE_DIRS[0], 'header.html'), 'w')
            header.write(content.encode('utf-8'))
            header.close()
            
            # Downloading footer
            response, content = http.request("http://www.20minutes.fr/api/v1/layout/footer?partner=eloue")
            content = smart_unicode(content, encoding='latin1')
            content = content.replace("<!-- {{PARTNER_ASSETS}} -->", "{% load compressed %}{% block tail %}{% compressed_js 'application' %}{% endblock %}")
            footer = open(os.path.join(settings.TEMPLATE_DIRS[0], 'footer.html'), 'w')
            footer.write(content.encode('utf-8'))
            footer.close()
        except (httplib2.HttpLib2Error, IOError), e:
            log.exception("Downloading footer and header failed")
        log.info('Starting downloading footer and header')
    
