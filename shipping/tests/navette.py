# -*- coding: utf-8 -*-
from unittest import TestCase

from shipping.navette import Navette, FileTransfer


class NavetteTest(TestCase):
    def setUp(self):
        self.client = Navette()

    @property
    def point(self):
        from django.contrib.gis.geos import Point
        return Point(48.856614, 2.3522219000000177)

    def test_get_pudo_departure(self):
        res = self.client.get_pudo(self.point, 'Departure')
        self.assertGreater(len(res), 0, res)
        self.assertEquals(res[0].CityName, 'PARIS', res)

    def test_get_pudo_arrival(self):
        res = self.client.get_pudo(self.point, 'Arrival')
        self.assertGreater(len(res), 0, res)
        self.assertEquals(res[0].CityName, 'PARIS', res)

    def test_get_price_from_partner(self):
        res = self.client.get_price_from_partner(23573, 25171)
        self.assertEquals(res.Amount, 3.9, res)
        self.assert_(getattr(res, 'Token', None), res)

    @property
    def now(self):
        from datetime import datetime
        try:
            from django.utils.timezone import get_default_timezone
            tz = get_default_timezone()
        except:
            import pytz
            tz = pytz.timezone('Europe/Paris')
        return datetime.now(tz=tz)

    def test_create_from_partner(self):
        order_details = {
            'DeliveryContactFirstName': 'TEST',
            'DeliveryContactLastName': 'Test',
            'DeliveryContactMail': 'test@test.com',
            'DeliveryContactMobil': '0648484848',
            'DeliveryContactPhone': '0148484848',
            'DeliverySiteAdress1': 'test',
            'DeliverySiteAdress2': 'test',
            'DeliverySiteCity': 'test',
            'DeliverySiteCountry': 'france',
            'DeliverySiteCountryCode': 'fr',
            'DeliverySiteName': 'test',
            'DeliverySiteZipCode': '75011',
            'DropOffContactFirstName': 'TEST',
            'DropOffContactLastName': 'Test',
            'DropOffContactMail': 'test@test.com',
            'DropOffContactMobil': '0648484848',
            'DropOffContactPhone': '0148484848',
            'DropOffSiteAdress1': 'test',
            'DropOffSiteAdress2': 'test',
            'DropOffSiteCity': 'test',
            'DropOffSiteCountry': 'france',
            'DropOffSiteCountryCode': 'fr',
            'DropOffSiteName': 'test',
            'DropOffSiteZipCode': '75011',
            'OrderContactFirstName': 'TEST',
            'OrderContactLastName': 'Test',
            'OrderContactMail': 'test@test.com',
            'OrderOrderContactMobil': '0648484848',
            'OrderContactCivility': 1,
            'OrderSiteAdress1': 'test',
            'OrderSiteAdress2': 'test',
            'OrderSiteCity': 'test',
            'OrderSiteCountry': 'france',
            'OrderSiteZipCode': '75011',
            'OrderDate': '2014-10-21T16:11:09+02:00',  # self.now.strftime('%FT%H:%M:%S%z'),
            'DeliverySiteId': 25608,
            'DropOffSiteId': 25894,
        }

        res = self.client.get_price_from_partner(
                order_details['DeliverySiteId'],
                order_details['DropOffSiteId'])
        res = self.client.create_from_partner(res.Token, order_details=order_details)
        return res

    def test_events(self):
        res = self.test_create_from_partner()
        res = self.client.get_events(res.NavetteCode)
        self.assert_(res)


class FileTransferTest(TestCase):
    def setUp(self):
        self.client = FileTransfer()

    def test_download_etiquette(self):
        client = Navette()

        order_details = {
            'DeliveryContactFirstName': 'TEST',
            'DeliveryContactLastName': 'Test',
            'DeliveryContactMail': 'test@test.com',
            'DeliveryContactMobil': '0648484848',
            'DeliveryContactPhone': '0148484848',
            'DeliverySiteAdress1': 'test',
            'DeliverySiteAdress2': 'test',
            'DeliverySiteCity': 'test',
            'DeliverySiteCountry': 'france',
            'DeliverySiteCountryCode': 'fr',
            'DeliverySiteName': 'test',
            'DeliverySiteZipCode': '75011',
            'DropOffContactFirstName': 'TEST',
            'DropOffContactLastName': 'Test',
            'DropOffContactMail': 'test@test.com',
            'DropOffContactMobil': '0648484848',
            'DropOffContactPhone': '0148484848',
            'DropOffSiteAdress1': 'test',
            'DropOffSiteAdress2': 'test',
            'DropOffSiteCity': 'test',
            'DropOffSiteCountry': 'france',
            'DropOffSiteCountryCode': 'fr',
            'DropOffSiteName': 'test',
            'DropOffSiteZipCode': '75011',
            'OrderContactFirstName': 'TEST',
            'OrderContactLastName': 'Test',
            'OrderContactMail': 'test@test.com',
            'OrderOrderContactMobil': '0648484848',
            'OrderContactCivility': 1,
            'OrderSiteAdress1': 'test',
            'OrderSiteAdress2': 'test',
            'OrderSiteCity': 'test',
            'OrderSiteCountry': 'france',
            'OrderSiteZipCode': '75011',
            'OrderDate': '2014-10-21T16:11:09+02:00',  # self.now.strftime('%FT%H:%M:%S%z'),
            'OrderId': 'B400003a-abcd',
            'DeliverySiteId': 25608,
            'DropOffSiteId': 25894,
        }

        res = client.get_price_from_partner(
                order_details['DeliverySiteId'],
                order_details['DropOffSiteId'])
        res = client.create_from_partner(res.Token, order_details=order_details)

        res = self.client.download_etiquette(res.NavettePDFUrl)
        import base64
        self.assert_(base64.b64decode(res), res)
