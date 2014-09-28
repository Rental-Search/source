from django.template import Library, Node

from django.template.defaultfilters import floatformat

register = Library()

@register.simple_tag
def price(obj, _from, to):
	try:
		return floatformat(obj.price(_from, to), 2)
	except:
		return obj.price