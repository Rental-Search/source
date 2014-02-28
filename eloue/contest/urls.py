# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('', 
	url(r'^$', 'contest.views.contest_publish_new_ad', name='contest_publish_new_ad'),
	url(r'^objet/$', 'contest.views.contest_publish_product', name='contest_publish_product'),
	url(r'^voiture/$', 'contest.views.contest_publish_car', name='contest_publish_car'),
	url(r'^logement/$', 'contest.views.contest_publish_real_estate', name='contest_publish_real_estate'),
	url(r'^bravo/$', 'contest.views.contest_congrat', name='contest_congrat'),
	url(r'^gamer/(?P<gamer_id>\d+)/$', 'contest.views.contest_edit_gamer', name='contest_edit_gamer'),
	url(r'^terms/$', 'contest.views.contest_terms', name='contest_terms'),
)