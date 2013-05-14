# -*- coding: utf-8 -*-
import datetime
import django.forms as forms

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib import messages
from django.db.models import Q


from eloue.accounts.forms import make_missing_data_form
from eloue.accounts.models import Patron, ProPackage


def patron_create_subscription(request):

	required_fields = ['username', 'is_professional', 'company_name', 'first_name', 'last_name', 'phones__phone', 'addresses__address1', 'addresses__zipcode', 'addresses__city', 'addresses__country', 'cvv', 'holder_name', 'card_number', 'expires']

	missing_fields, missing_form = make_missing_data_form(None, required_fields)

	class NewSubscriptionForm(missing_form):
		email = forms.EmailField(label="Email", max_length=75, required=True)

		class Meta:
			fieldsets = [
				('member', {
	                'fields': ['subscription'], 
	                'legend': 'Choix de l\'offre'}),
	            ('member', {
	                'fields': ['is_professional', 'company_name', 'username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'avatar', 'godfather_email','date_of_birth', 'place_of_birth'], 
	                'legend': 'Informations sur l\'entreprise'}),
	            ('driver_info', {
	                'fields': ['drivers_license_number', 'drivers_license_date'],
	                'legend': 'Permis de conduire'}),
	            ('contacts', {
	                'fields': ['addresses', 'addresses__address1', 'addresses__zipcode', 'addresses__city', 'addresses__country', 'phones', 'phones__phone'], 
	                'legend': 'Vos coordonnées'}),
	            ('payment', {
	                'fields': ['cvv', 'expires', 'holder_name', 'card_number', ],
	                'legend': 'Coordonnées bancaires'
	                }),
	        ]


	form = NewSubscriptionForm(request.POST or None)

	if form.is_valid():
		new_patron = Patron.objects.create_user(
			form.cleaned_data['username'], 
			form.cleaned_data['email']
		)
		form.instance = new_patron
		patron = form.save()[0]
		patron.default_number = patron.phones.all()[0]
		patron.save()
		messages.success(request, 'Create user successed')

		form = NewSubscriptionForm()

		

	if form.errors:
		messages.error(request, 'Create user fail')



	return render_to_response(
				"accounts/admin/patron_create_subscription.html",
				{},
				RequestContext(request, {'form': form,}),)