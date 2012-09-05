from django.conf.urls.defaults import *
from eloue.reporting.admin_views import stats, top_patron_city, top_product_city, top_product_category, top_booking_patron


urlpatterns = patterns('',
    url(r'^all/$', stats, name="stats"),
    url(r'^patron/top_city/$', top_patron_city, name="top_patron_city"),
    url(r'^booking/top_patron/$', top_booking_patron, name="top_booking_patron"),
    url(r'^product/top_city/$', top_product_city, name="top_product_city"),
    url(r'^product/top_category/$', top_product_category, name="top_product_category"),
)