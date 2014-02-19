# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.views.decorators.cache import never_cache
from django.utils import simplejson
from eloue.decorators import secure_required
from eloue.products.models import Product
from eloue.products.forms import ProductForm, CarProductForm, RealEstateForm
from eloue.accounts.forms import EmailAuthenticationForm
from eloue.contest.wizard import ContestProductWizard
from eloue.contest.forms import GamerForm
from eloue.contest.models import Gamer, ProductGamer

@never_cache
@secure_required
def contest_publish_new_ad(request, *args, **kwargs):
	return render(request, 'contest/contest_publish_new_ad.html', {})

@never_cache
@secure_required
def contest_publish_product(request, *args, **kwargs):
    wizard = ContestProductWizard([ProductForm, EmailAuthenticationForm])
    return wizard(request, *args, **kwargs)

@never_cache
@secure_required
def contest_publish_car(request, *args, **kwargs):
	wizard = ContestProductWizard([CarProductForm, EmailAuthenticationForm])
	return wizard(request, *args, **kwargs)

@never_cache
@secure_required
def contest_publish_real_estate(request, *args, **kwargs):
	wizard = ContestProductWizard([RealEstateForm, EmailAuthenticationForm])
	return wizard(request, *args, **kwargs)


@never_cache
@secure_required
def contest_congrat(request, *args, **kwargs):
	try:
		gamer = request.user.gamer_set.all()[0]
		product_gamer = ProductGamer.objects.filter(gamer=gamer).order_by('-created_at')[0]
		gamer_id = gamer.pk
	except:
		raise Http404
	return render(request, 'contest/contest_congrat.html', {'gamer_id': gamer_id, 'product': product_gamer.product})

@never_cache
@secure_required
def contest_terms(request, *arg, **kwargs):
	return render(request, 'contest/contest_terms.html', {})


def contest_edit_gamer(request, gamer_id, *args, **kwargs):
	if not request.is_ajax() and request.POST:
		raise Http404
	try:
		gamer = Gamer.objects.get(pk=gamer_id)
	except:
		raise Http404
	if request.user.pk != gamer.patron.pk:
		print 'not user'
		raise Http404
	form = GamerForm(request.POST, instance=gamer)
	if form.is_valid():
		gamer = form.save()
		gamer_dict = gamer.__dict__
		gamer_dict.pop('_state')
		gamer_dict.pop('_patron_cache') if gamer_dict.has_key('_patron_cache') else False
		json = simplejson.dumps(gamer_dict)
		return HttpResponse(json, mimetype="application/json")
	else:
		json = simplejson.dumps(form.errors)
		return HttpResponse(form.errors, mimetype="application/json")

		
