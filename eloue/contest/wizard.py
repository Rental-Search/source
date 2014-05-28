from django.shortcuts import redirect

from accounts.forms import EmailAuthenticationForm
from products.wizard import ProductWizard
from products.forms import ProductForm
from products.models import Product, Picture, Alert
from products.choices import UNIT
from contest.models import Gamer, ProductGamer

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

		try:
			gamer = Gamer.objects.get(patron=self.product.owner)
		except:
			gamer = Gamer.objects.create(patron=self.product.owner)
		
		ProductGamer.objects.create(product=self.product, gamer=gamer)

		return redirect('contest.views.contest_congrat')