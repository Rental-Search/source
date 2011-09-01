# -*- coding: utf-8 -*-

import json
import re
import traceback

from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.csrf.middleware import csrf_exempt

from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpUnauthorized, HttpBadRequest

from eloue.products.models import Product, Price, UNIT
from eloue.api.resources import OAuthentication, OAuthAuthorization


def is_authenticated(request):
    authentication = OAuthentication()
    authorization = OAuthAuthorization()
    return authentication.is_authenticated(request) and authorization._is_valid(request)


@csrf_exempt
def update_product_prices(request):

    from dateutil import parser

    try:
        if request.method == 'POST':
            if not is_authenticated(request):
                return HttpUnauthorized()

            data = json.loads(request.raw_post_data)
            ids = [s.split("/")[-2] for s in data["products"]]
            products = Product.objects.filter(id__in=ids)

            prices_dicts = [{"unit": UNIT.enum_dict[p["unit"]],
                             "amount":p["amount"],
                             "currency":p["currency"],
                             "started_at": parser.parse(p["started_at"]).date(),
                             "ended_at": parser.parse(p["ended_at"]).date()}
                             for p in data["prices"]]

            for product in products:
                product.prices.all().delete()
                print prices_dicts
                for price_dict in prices_dicts:
                    Price(product=product, **price_dict).save()

            return HttpResponse()
        else:
            return HttpBadRequest()
    except Exception, e:
        print e
        traceback.print_exc()
