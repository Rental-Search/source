# coding=utf-8
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
            tz=get_default_timezone()
        except:
            import pytz
            tz = pytz.timezone('Europe/Paris')
        return datetime.now(tz=tz)

    def test_create_from_partner(self):
        order_details = self.client._create_order_details()
        order_details.DeliveryContactFirstName = 'TEST'
        order_details.DeliveryContactLastName = 'Test'
        order_details.DeliveryContactMail = 'test@test.com'
        order_details.DeliveryContactMobil = '0648484848'
        order_details.DeliveryContactPhone = '0148484848'
        order_details.DeliverySiteAdress1 = 'test'
        order_details.DeliverySiteAdress2 = 'test'
        #order_details.DeliverySiteAdress3 = ''
        order_details.DeliverySiteCity = 'test'
        order_details.DeliverySiteCountry = 'france'
        order_details.DeliverySiteCountryCode = 'fr'
        order_details.DeliverySiteName = 'test'
        order_details.DeliverySiteZipCode = '75011'
        order_details.DropOffContactFirstName = 'TEST'
        order_details.DropOffContactLastName = 'Test'
        order_details.DropOffContactMail = 'test@test.com'
        order_details.DropOffContactMobil = '0648484848'
        order_details.DropOffContactPhone = '0148484848'
        order_details.DropOffSiteAdress1 = 'test'
        order_details.DropOffSiteAdress2 = 'test'
        #order_details.DropOffSiteAdress3 = ''
        order_details.DropOffSiteCity = 'test'
        order_details.DropOffSiteCountry = 'france'
        order_details.DropOffSiteCountryCode = 'fr'
        order_details.DropOffSiteName = 'test'
        order_details.DropOffSiteZipCode = '75011'
        order_details.OrderContactFirstName = 'TEST'
        order_details.OrderContactLastName = 'Test'
        order_details.OrderContactMail = 'test@test.com'
        order_details.OrderOrderContactMobil = '0648484848'
        order_details.OrderContactCivility = 1
        order_details.OrderSiteAdress1 = 'test'
        order_details.OrderSiteAdress2 = 'test'
        #order_details.OrderSiteAdress3 = ''
        order_details.OrderSiteCity = 'test'
        order_details.OrderSiteCountry = 'france'
        order_details.OrderSiteZipCode = '75011'
        order_details.OrderDate = '2014-10-21T16:11:09+02:00'# self.now.strftime('%FT%H:%M:%S%z')
        order_details.OrderId = 'B400003a-abcd'
        #order_details.ParcelWeight = 1
        order_details.DeliverySiteId = 25608
        order_details.DropOffSiteId = 25894

        res = self.client.get_price_from_partner(order_details.DeliverySiteId, order_details.DropOffSiteId)
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

        order_details = client._create_order_details()
        order_details.DeliveryContactFirstName = 'TEST'
        order_details.DeliveryContactLastName = 'Test'
        order_details.DeliveryContactMail = 'test@test.com'
        order_details.DeliveryContactMobil = '0648484848'
        order_details.DeliveryContactPhone = '0148484848'
        order_details.DeliverySiteAdress1 = 'test'
        order_details.DeliverySiteAdress2 = 'test'
        #order_details.DeliverySiteAdress3 = ''
        order_details.DeliverySiteCity = 'test'
        order_details.DeliverySiteCountry = 'france'
        order_details.DeliverySiteCountryCode = 'fr'
        order_details.DeliverySiteName = 'test'
        order_details.DeliverySiteZipCode = '75011'
        order_details.DropOffContactFirstName = 'TEST'
        order_details.DropOffContactLastName = 'Test'
        order_details.DropOffContactMail = 'test@test.com'
        order_details.DropOffContactMobil = '0648484848'
        order_details.DropOffContactPhone = '0148484848'
        order_details.DropOffSiteAdress1 = 'test'
        order_details.DropOffSiteAdress2 = 'test'
        #order_details.DropOffSiteAdress3 = ''
        order_details.DropOffSiteCity = 'test'
        order_details.DropOffSiteCountry = 'france'
        order_details.DropOffSiteCountryCode = 'fr'
        order_details.DropOffSiteName = 'test'
        order_details.DropOffSiteZipCode = '75011'
        order_details.OrderContactFirstName = 'TEST'
        order_details.OrderContactLastName = 'Test'
        order_details.OrderContactMail = 'test@test.com'
        order_details.OrderOrderContactMobil = '0648484848'
        order_details.OrderContactCivility = 1
        order_details.OrderSiteAdress1 = 'test'
        order_details.OrderSiteAdress2 = 'test'
        #order_details.OrderSiteAdress3 = ''
        order_details.OrderSiteCity = 'test'
        order_details.OrderSiteCountry = 'france'
        order_details.OrderSiteZipCode = '75011'
        order_details.OrderDate = '2014-10-21T16:11:09+02:00'# self.now.strftime('%FT%H:%M:%S%z')
        order_details.OrderId = 'B400003a-abcd'
        #order_details.ParcelWeight = 1
        order_details.DeliverySiteId = 25608
        order_details.DropOffSiteId = 25894

        res = client.get_price_from_partner(order_details.DeliverySiteId, order_details.DropOffSiteId)
        res = client.create_from_partner(res.Token, order_details=order_details)

        res = self.client.download_etiquette(res.NavettePDFUrl)
        import base64
        self.assert_(base64.b64decode(res), res)
