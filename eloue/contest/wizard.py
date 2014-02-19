from eloue.products.wizard import ProductWizard
from eloue.accounts.forms import EmailAuthenticationForm
from eloue.products.forms import ProductForm
from eloue.products.models import Product, Picture, UNIT, Alert

from eloue.contest.models import Gamer, ProductGamer

from django.shortcuts import redirect

class ContestProductWizard(ProductWizard):

	def __init__(self, *args, **kwargs):
		super(ContestProductWizard, self).__init__(*args, **kwargs)


	def get_template(self, step):
		if issubclass(self.form_list[step], EmailAuthenticationForm):
			return 'contest/contest_auth_login.html'
		elif issubclass(self.form_list[step], ProductForm):
			return 'contest/contest_product_create.html'
		else:
			return 'contest/contest_auth_missing.html'

	def done(self, request, form_list):
		super(ContestProductWizard, self).done(request, form_list)
		patron = request.user

		#Create product
		product_form = form_list[0]
		product_form.instance.owner = self.new_patron
		product_form.instance.address = self.new_address
		product_form.instance.phone = self.new_phone
		product = product_form.save()

		try:
			gamer = Gamer.objects.get(patron=product.owner)
		except:
			gamer = Gamer.objects.create(patron=product.owner)
		
		ProductGamer.objects.create(product=product, gamer=gamer)

		for unit in UNIT.keys():
			field = "%s_price" % unit.lower()
			if field in product_form.cleaned_data and product_form.cleaned_data[field]:
				product.prices.create(
					unit=UNIT[unit],
					amount=product_form.cleaned_data[field]
				)
        
		picture_id = product_form.cleaned_data.get('picture_id')
		if picture_id:
			product.pictures.add(Picture.objects.get(pk=picture_id))

		return redirect('contest.views.contest_congrat')