# -*- coding: utf-8 -*-
import re

from datetime import datetime, timedelta
from httplib2 import Http
from lxml import objectify
from urllib import urlencode, quote_plus

from django.utils.encoding import smart_str

from . import BaseSource, Product


class SourceClass(BaseSource):
    def build_xml(self, params):
        xml = """<SearchRQ>
            <Credentials username="eloue_fr" password="eloue" remoteIp="127.0.0.1" />
            <PickUp>
             <Location id="%(location)s" />
             <Date year="%(pickup_year)d" month="%(pickup_month)d" day="%(pickup_day)d" hour="%(pickup_hour)d" minute="%(pickup_minute)d"/>
            </PickUp>
            <DropOff>
             <Location id="%(location)s" />
             <Date year="%(dropoff_year)d" month="%(dropoff_month)d" day="%(dropoff_day)d" hour="%(dropoff_hour)d" minute="%(dropoff_minute)d"/>
            </DropOff>
            <DriverAge>%(age)d</DriverAge>
           </SearchRQ>""" % params
        return re.sub(r'\n\s*', '', xml)

    def get_cities(self):
        cities = []
        for location in ['France - Continent', 'France - Corse']:
             response, content = Http().request("http://www.elocationdevoitures.fr/service/ServiceRequest.do?xml=%s" % quote_plus('<PickUpCityListRQ><Credentials username="eloue_fr" password="eloue" remoteIp="127.0.0.1" /><Country>%(country)s</Country></PickUpCityListRQ>' % {'country': location}))
             root = objectify.fromstring(content)
             for city in root.xpath('//City'):
                 cities.append({'location': location, 'city': smart_str(city.pyval)})
        return cities
    
    def get_locations(self):
        locations = []
        for city in self.get_cities():
            response, content = Http().request("http://www.elocationdevoitures.fr/service/ServiceRequest.do?xml=%s" % quote_plus('<PickUpLocationListRQ><Credentials username="eloue_fr" password="eloue" remoteIp="127.0.0.1" /><Country>%(location)s</Country><City>%(city)s</City></PickUpLocationListRQ>' % city))
            root = objectify.fromstring(content)
            for location in root.xpath('//Location'):
                locations.append({
                    'id': location.get('id'),
                    'name': location.pyval,
                    'city': city['city'],
                    'country': city['location'],
                })
        return locations
    
    def get_docs(self):
        docs = []
        pickup_date = datetime.now() + timedelta(days=7)
        dropoff_date = pickup_date + timedelta(days=1)
        for location in self.get_locations():
            response, content = Http().request("http://www.elocationdevoitures.fr/service/ServiceRequest.do?%s" % urlencode({
                'xml': self.build_xml({ 'age': 25, 'location': location['id'],
                    'pickup_year': pickup_date.year, 'pickup_month': pickup_date.month, 'pickup_day': pickup_date.day, 'pickup_hour': 12, 'pickup_minute': 30,
                    'dropoff_year': dropoff_date.year, 'dropoff_month': dropoff_date.month, 'dropoff_day': dropoff_date.day, 'dropoff_hour': 12, 'dropoff_minute': 30,
                })
            }))
            root = objectify.fromstring(content)
            for match in root.xpath('//Match'):
                lat, lon = BaseSource().get_coordinates("%s" % (match.Route.PickUp.Location.get('locName'),))
                docs.append(Product({
                    'id': '%s.%s' % (SourceClass().get_prefix(), match.Vehicle.get('id')),
                    'summary': match.Vehicle.Name.pyval,
                    'description': match.Vehicle.Description.pyval,
                    'categories': ['auto-et-moto', 'voiture'],
                    'lat': lat, 'lng': lon,
                    'city': match.Route.PickUp.Location.get('locName'),
                    'price': match.Price.pyval,
                    'owner': 'elocationdevoitures', 
                    'owner_url': 'http://www.elocationdevoitures.fr/',
                    'url': 'http://www.elocationdevoitures.fr/SearchResults.do?country=%(country)s&city=%(city)s&location=%(location)s&dropLocation=%(location)s&puYear=%(pickup_year)d&puMonth=%(pickup_month)d&puDay=%(pickup_day)d&puHour=12&puMinute=20&doYear=%(dropoff_year)d&doMonth=%(dropoff_month)d&doDay=%(dropoff_day)d&doHour=12&doMinute=30&driversAge=%(age)d&affiliateCode=eloue_fr' % {
                        'age': 25, 'location': location['id'], 'city': location['city'], 'country': location['country'],
                        'pickup_year': pickup_date.year, 'pickup_month': pickup_date.month, 'pickup_day': pickup_date.day, 'pickup_hour': 12, 'pickup_minute': 30,
                        'dropoff_year': dropoff_date.year, 'dropoff_month': dropoff_date.month, 'dropoff_day': dropoff_date.day, 'dropoff_hour': 12, 'dropoff_minute': 30,
                    },
                    'thumbnail': match.Vehicle.ImageURL.pyval,
                    'django_id': 'jigsaw.%s' % match.Vehicle.get('id')
                }))
        return docs
    
    def get_prefix(self):
        return 'source.jigsaw'
    
