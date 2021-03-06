# -*- coding: utf-8 -*-

import json
import traceback

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from tastypie.http import HttpUnauthorized, HttpBadRequest

from products.models import Product, Price
from products.choices import UNIT
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

            data = json.loads(request.body)
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
                for price_dict in prices_dicts:
                    Price(product=product, **price_dict).save()

            return HttpResponse()
        else:
            return HttpBadRequest()
    except Exception:
        traceback.print_exc()
