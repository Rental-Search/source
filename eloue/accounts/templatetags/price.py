from django.template import Library, Node

register = Library()

@register.simple_tag
def price(obj, _from, to):
	return obj.price(_from, to)