from django.conf import settings
from django.conf.urls import *

from eloue.api.resources import api_v1
from eloue.api import views

urlpatterns = patterns('',
    url(r'^1.0/update_product_prices/$', views.update_product_prices, name='update_product_prices'),
    url(r'^', include(api_v1.urls)),
)
