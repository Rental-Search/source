# -*- coding: utf-8 -*-
import datetime
import django.forms as forms

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.contrib import messages
from django.db.models import Q
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.translation import ugettext as _
from django.core import urlresolvers


from accounts.forms import make_missing_data_form
from accounts.models import Patron, ProPackage

from payments.slimpay_payment import SlimPayManager
from payments.models import SlimPayMandateInformation
from payments.slimpay_forms import BridgeForm

def patron_create_subscription(request):

	required_fields = ['username', 'is_professional', 'company_name', 'first_name', 'last_name', 'phones__phone', 'addresses__address1', 'addresses__zipcode', 'addresses__city', 'addresses__country']

	missing_fields, missing_form = make_missing_data_form(None, required_fields)

	class NewSubscriptionForm(missing_form):
		email = forms.EmailField(label="Email", max_length=75, required=True)

		class Meta:
			fieldsets = [
				('member', {
	                'fields': ['subscription'], 
	                'legend': 'Choix de l\'abonnement'}),
	            ('member', {
	                'fields': ['is_professional', 'company_name', 'username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'avatar', 'godfather_email','date_of_birth', 'place_of_birth'], 
	                'legend': 'Informations sur l\'entreprise'}),
	            ('driver_info', {
	                'fields': ['drivers_license_number', 'drivers_license_date'],
	                'legend': 'Permis de conduire'}),
	            ('address', {
	                'fields': ['addresses', 'addresses__address1', 'addresses__zipcode', 'addresses__city', 'addresses__country'], 
	                'legend': 'Adresse'}),
	            ('phone', {
	                'fields': ['phones__phone'], 
	                'legend': 'Numéro de téléphone'}),
	        ]

		def __init__(self, *args, **kwargs):
			super(NewSubscriptionForm, self).__init__(*args, **kwargs)
			now = datetime.datetime.now()
			self.fields['is_professional'].initial = True
			self.fields['is_professional'].widget = forms.HiddenInput()
			self.fields['phones__phone'].label = 'Numéro'
			self.fields['subscription'] = forms.ModelChoiceField(label='Abonnement', required=True,
	            queryset=ProPackage.objects.filter(
	                Q(valid_until__isnull=True)|Q(valid_until__gte=now) 
	            )
	        )

		
		def clean_email(self):
			if Patron.objects.filter(email=self.cleaned_data['email']).exists():
				raise forms.ValidationError(_(u"Cett email est déjà pris."))
			return self.cleaned_data['email']

		def clean_subscription(self):
			print form.cleaned_data['subscription'].pk
			return form.cleaned_data['subscription']

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

		patron.subscribe(form.cleaned_data['subscription'])
		patron.current_subscription.save()

		#redirect to to slimplay only if it's not free
		if form.cleaned_data['subscription'].pk == 9:
			return redirect(urlresolvers.reverse('admin:accounts_subscription_change', args=(patron.current_subscription.pk,)))
		
		else:
			slimpay_mandate_info = SlimPayMandateInformation.objects.create(patron=new_patron)

			blob = slimpay_mandate_info.blob()

			bridge_form = BridgeForm(initial={'blob': blob})

			return render_to_response('payments/admin/slimpay_bridge.html', RequestContext(request, {'form': bridge_form}))

		

	if form.errors:
		messages.error(request, 'Create user fail')



	return render_to_response(
				"accounts/admin/patron_create_subscription.html",
				{},
				RequestContext(request, {'form': form,}),)


patron_create_subscription = staff_member_required(patron_create_subscription)