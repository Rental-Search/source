# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.views.decorators.cache import never_cache
from eloue.decorators import secure_required
from eloue.products.forms import ProductForm, CarProductForm, RealEstateForm
from eloue.accounts.forms import EmailAuthenticationForm
from eloue.contest.wizard import ContestProductWizard

@never_cache
@secure_required
def contest_publish_new_add(request, *args, **kwargs):
	return render(request, 'contest/contest_publish_new_add.html', {})

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
	return render(request, 'contest/contest_congrat.html', {})

@never_cache
@secure_required
def contest_terms(request, *arg, **kwargs):
	return render(request, 'contest/contest_terms.html', {})