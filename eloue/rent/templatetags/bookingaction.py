# -*- coding: utf-8 -*-
import urllib

from django import template
from django.utils.safestring import mark_safe
from django.template import Context, Template, RequestContext
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.conf import settings

from eloue.rent.models import BOOKING_STATE


register = template.Library()

class ActionWidget(object):
	def render(self, request, booking):
		raise NotImplementedError

class TemplateWidgetAction(ActionWidget):
	def render(self, request, context_dict):
		try:
			return self.template.render(
				RequestContext(
					request, context_dict
				)
			)
		except AttributeError:
			raise NotImplementedError(
				'{classname}.template attribute should be a Template instance'.format(
					classname=self.__class__.__name__
				)
			)


class LinkWidget(TemplateWidgetAction):
	template = Template(
		ur'{% load i18n %}'
		'<a href="{{ url }}">{% trans text %}</a>'
	)

	def __init__(self, url_builder, text):
		self.url_builder = url_builder
		self.text = text

	def render(self, request, booking):
		context_dict = {
			'url': self.url_builder(request, booking), 
			'text': self.text 
		}
		return super(LinkWidget,self).render(request, context_dict)


class PostForm(TemplateWidgetAction):
	template = Template(
		ur'{% load i18n %}'
		'<form action="{{url}}" method="post">'
		'{% csrf_token %}'
		'<input type="hidden" name="state" value={{ state }}/>'
		'<button>{% trans text %}</button>'
		'</form>'
	)

	def __init__(self, text, view_name, state):
		self.text = text
		self.view_name = view_name
		self.state = state

	def render(self, request, booking):
		context_dict = {
			'url': reverse(
				self.view_name, 
				kwargs={'booking_id':booking.pk.hex}
			), 
			'booking': booking,
			'state': self.state,
			'text': self.text,
		}
		return super(PostForm, self).render(request, context_dict)


Accept = PostForm('Accepter', 'eloue.rent.views.booking_accept', BOOKING_STATE.PENDING)
Refuse = PostForm('Refuser', 'eloue.rent.views.booking_refuse', BOOKING_STATE.REJECTED)
Cancel = PostForm('Annuler', 'eloue.rent.views.booking_cancel', BOOKING_STATE.CANCELED)
Close = PostForm(u'Clôturer', 'eloue.rent.views.booking_close', BOOKING_STATE.CLOSING)
Incident = PostForm('Signaler une incident', 'eloue.rent.views.booking_incident', BOOKING_STATE.INCIDENT)

PaypalAuthorize = LinkWidget(
	url_builder=lambda request, booking: settings.PAYPAL_COMMAND%urllib.urlencode({
					'cmd': '_ap-preapproval',
		        	'preapprovalkey': booking.preapproval_key
                }), 
	text='Authorizer payment'
)


SendMessageToOwner = LinkWidget(
	url_builder=lambda request, booking: reverse(
		'eloue.products.views.message_create', 
		kwargs={
			'product_id': booking.product.pk,
			'recipient_id': booking.owner.pk
		}),
	text=u'Envoyer un message au propriétaire'
)


SendMessageToBorrower = LinkWidget(
	url_builder=lambda request, booking: reverse(
		'eloue.products.views.message_create', 
		kwargs={
			'product_id': booking.product.pk,
			'recipient_id': booking.owner.pk
		}),
	text=u'Envoyer un message au locataire'
)

borrower = {
    'AUTHORIZING': (Cancel, PaypalAuthorize, SendMessageToOwner),
    'authorized': (Cancel, SendMessageToOwner, ),
    'REJECTED': (SendMessageToOwner, ),
    'CANCELED': (), 
   	'PENDING': (Cancel, ),
    'ONGOING': (Incident, ), 
    'ENDED': (Incident, ),
    'INCIDENT': (), 
    'REFUNDED': (),
    'DEPOSIT': (),
    'CLOSING': (),
    'CLOSED': (), 
    'OUTDATED': (),
}

owner = {
    'AUTHORIZING': (), 
    'authorized': (Accept, Refuse, SendMessageToBorrower),
    'REJECTED': (),
    'CANCELED': (), 
   	'PENDING': (Cancel, ),
    'ONGOING': (Incident, ), 
    'ENDED': (Close, Incident, ),
    'INCIDENT': (), 
    'REFUNDED': (),
    'DEPOSIT': (),
    'CLOSING': (),
    'CLOSED': (), 
    'OUTDATED': (),
}

@register.simple_tag
def bookingaction(request, booking):
	actions = borrower if booking.borrower == request.user else owner
	possible_actions = actions[booking.state]
	return u'<td colspan={len}>{actions}</td>'.format(
		len=len(possible_actions),
		actions=u' - '.join([action.render(request, booking) for action in possible_actions])
	)
	return PaypalAuthorize.render(request, booking)+Accept.render(request, booking)