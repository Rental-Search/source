def post_save_booking(sender, instance, created, **kwargs):
	instance.sites.add(*instance.product.sites.all())