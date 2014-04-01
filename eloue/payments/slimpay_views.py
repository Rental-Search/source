# -*- coding: utf-8 -*-
from django.http import HttpResponse


from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render_to_response

from eloue.payments.slimpay_payment import SlimPayManager
from eloue.payments.slimpay_forms import BridgeForm
from eloue.payments.models import SlimPayMandateInformation

@require_POST
@csrf_exempt
def clientInitialization(request):

	# parameters
	# transactionStatus=success
	# transactionErrorCode=0
	# transactionId=1395930764668
	# requestType=init
	# siteId=elouetest

	return HttpResponse()

def return_initial(request):
	return HttpResponse('<h1>Initial slimpay return</h1>')

@require_POST
@csrf_exempt
def notify_response(request):
	form = BridgeForm(request.POST or None)

	if form.is_valid():
		slimpay_manager = SlimPayManager()

		response = slimpay_manager.decodeBlob(form.cleaned_data['blob'])

		SlimPayMandateInformation.objects.create(
				RUM = response.get('RUM'),
				signatureDate=response.get('signatureDate'),
				mandateFileName=response.get('mandateFileName'),
				transactionId=response.get('transactionId'),
				patron_id=2345
			)

	# parameters
	# transactionStatus=success
	# transactionErrorCode=0
	# signatureOperationResult=1
	# signatureDate=2014-03-20 12:22:20
	# mandateScore=0
	# mandateFileName=Mandate-002429432.pdf
	# transactionId=transaction3
	# requestType=mandate
	# siteId=elouetest
	# clientReference=client1
	# RUM=SLMP002429432
	# companyName=company1
	# organizationId=ORG1
	# title=mr
	# firstName=prénom
	# lastName=nom
	# email=prenom.nom@test-mail.pn
	# bic=SLMPFRP1
	# iban=FR7616348000019000000000048
	# invoiceLine1=94 avenue Felix Faure
	# invoicePostalCode=75015
	# invoiceCity=Paris
	# invoiceCountry=FR

	return HttpResponse()
