# -*- coding: utf-8 -*-
from suds.client import Client
from suds.cache import DocumentCache

from django.utils.functional import cached_property


class WsdlClientBase(object):
    wsdl_proxy = None

    @cached_property
    def client(self):
        api = Client(self.url)
        if self.wsdl_proxy is not None:
            api.set_options(proxy=self.wsdl_proxy)
        api.set_options(cache=DocumentCache())
        return api


class Navette(WsdlClientBase):
    url = 'http://test-web-navette.pickup.fr/v1/Navette.svc?wsdl'

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
