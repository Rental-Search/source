from django.conf.urls.defaults import *
from eloue.reporting.admin_views import stats, stats_by_patron, stats_by_product, stats_by_category, stats_by_city, stats_by_patron_detail, stats_by_product_detail, stats_by_category_detail, stats_by_city_detail


urlpatterns = patterns('',
    url(r'^all/$', stats, name="stats"),
    url(r'^patron/$', stats_by_patron, name="stats_by_patron"),
    url(r'^patron/(?P<patron_id>\d+)/$', stats_by_patron_detail, name="stats_by_patron_detail"),
    url(r'^product/$', stats_by_product, name="stats_by_product"),
    url(r'^product/(?P<product_id>\d+)/$', stats_by_product_detail, name="stats_by_product_detail"),
    url(r'^category/$', stats_by_category, name="stats_by_category"),
    url(r'^category/(?P<category_id>\d+)/$', stats_by_category_detail, name="stats_by_category_detail"),
    url(r'^city/$', stats_by_city, name="stats_by_city"),
    url(r'^city/(?P<city>[-\w]+)/$', stats_by_city_detail, name="stats_by_city_detail")
)