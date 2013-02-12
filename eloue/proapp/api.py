
from tastypie.api import Api
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource

from eloue.products.models import Product

class UserAuthorization(Authorization):
	def apply_limits(self, request, object_list):
		if request and hasattr(request, 'user'):
			return object_list.filter(owner=request.user)
		

class ProductResource(ModelResource):
	class Meta:
		queryset = Product.objects.all()
		resource_name = 'products/product'
		excludes = ['currency', 'payment_type']
		ordering = ['created_at']
		authorization = UserAuthorization()


api_v1 = Api(api_name='1.0')
api_v1.register(ProductResource())