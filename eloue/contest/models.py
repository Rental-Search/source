from datetime import datetime
from django.db import models
from eloue.products.models import Product

class ProductGamer(models.Model):
	product = models.ForeignKey(Product)
	birthday = models.DateTimeField(null=True)
	created_at = models.DateTimeField(editable=False)
	
	def save(self, *args, **kwargs):
		if not self.created_at:
			self.created_at = datetime.now()
		super(ProductGamer, self).save(*args, **kwargs)