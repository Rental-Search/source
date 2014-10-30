# -*- coding: utf-8 -*-
from suds.client import Client
from suds.cache import DocumentCache

from django.utils.functional import cached_property


class WsdlClientBase(object):
    @cached_property
    def client(self):
        api = Client(self.url)
        api.set_options(cache=DocumentCache())
        return api


class Navette(WsdlClientBase):
    url = 'http://test-web-navette.pickup.fr/v1/Navette.svc?wsdl'

    @cached_property
    def search_pudo_type(self):
        return self.client.factory.create('ns1:SearchPudoType')

    def get_pudo(self, point, pudo_type):
        request = self.client.factory.create('ns0:PudoRequest')
        request.lat = point.x
        request.lng = point.y
        request.SearchPudoType = getattr(self.search_pudo_type, pudo_type)
        res = self.client.service.GetPudo(request)
        if res.Pudos:
            return res.Pudos.Pudo
        else:
            return []

    def get_price_from_partner(self, departure_siteid, arrival_siteid):
        request = self.client.factory.create('ns0:PricesRequestPartner')
        request.selectedDeparturePudoSiteId = departure_siteid
        request.selectedArrivalPudoSiteId = arrival_siteid
        return self.client.service.GetPricesFromPartner(request)

    def _create_order_details(self):
        return self.client.factory.create('ns0:NavetteInput')

    def _get_order_details(self, **kwargs):
        order_details = self._create_order_details()
        for key, value in kwargs.iteritems():
            setattr(order_details, key, value)
        return order_details

    def create_from_partner(self, token, order_details=None, insurance_enabled=False, **kwargs):
        request = self.client.factory.create('ns0:CreateRequest')
        request.Token = token
        request.WithOption = insurance_enabled
        request.OrderDetails = self._get_order_details(**kwargs) if order_details is None else order_details
        return self.client.service.CreateFromPartner(request)

    def get_events(self, ref):
        return self.client.service.GetEventsByReferenceColis(ref).EventColis


class FileTransfer(WsdlClientBase):
    url = 'http://test-web-navette.pickup.fr/v1/FileTransfer.svc?wsdl'

    def download_etiquette(self, etiquette_filename):
        return self.client.service.DownloadEtiquette(etiquette_filename)
