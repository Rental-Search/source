# -*- coding: utf-8 -*-
from suds.client import Client
from suds.cache import DocumentCache

from django.utils.functional import cached_property


class WsdlClientBase(object):
    @cached_property
    def client(self):
        proxy_hosts = dict(http='ec2-54-77-217-241.eu-west-1.compute.amazonaws.com:8080')
        api = Client(self.url)
        api.set_options(proxy=proxy_hosts)
        api.set_options(cache=DocumentCache())
        return api


class Navette(WsdlClientBase):
    from django.conf import settings
    url = getattr(settings, 'NAVETTE_ENDPOINT', None)

    if not url:
        raise InvalidBackend("NAVETTE_ENDPOINT not set.")

    def get_pudo(self, point, pudo_type):
        res = self.client.service.GetPudo({
            'lat': point.x,
            'lng': point.y,
            'SearchPudoType': pudo_type
        })
        if res.Pudos:
            return res.Pudos.Pudo
        else:
            return []

    def get_price_from_partner(self, departure_siteid, arrival_siteid):
        return self.client.service.GetPricesFromPartner({
            'selectedDeparturePudoSiteId': departure_siteid,
            'selectedArrivalPudoSiteId': arrival_siteid,
        })

    def create_from_partner(self, token, order_details, insurance_enabled=False):
        return self.client.service.CreateFromPartner({
            'Token': token,
            'WithOption': insurance_enabled,
            'OrderDetails': order_details
        })

    def get_events(self, ref):
        return self.client.service.GetEventsByReferenceColis(ref).EventColis


class FileTransfer(WsdlClientBase):
    url = 'http://test-web-navette.pickup.fr/v1/FileTransfer.svc?wsdl'

    def download_etiquette(self, etiquette_filename):
        return self.client.service.DownloadEtiquette(etiquette_filename)
