# -*- coding: utf-8 -*-
import urllib

from django import template
from django.utils.safestring import mark_safe
from django.template import Context, Template, RequestContext
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.conf import settings

from rent.models import BOOKING_STATE


register = template.Library()

class ActionWidget(object):
	def render(self, request, booking):
		raise NotImplementedError

	def condition(self, request, booking):
		return True

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
		'<li><a href="{{ url }}">{% trans text %}</a></li>'
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
		'<li><form action="{{url}}" method="post">'
		'{% csrf_token %}'
		'<input type="hidden" name="state" value="{{ state }}"/>'
		'<button class="btn-booking-action {{ state }}">{% trans text %}</button>'
		'</form></li>'
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


Accept = PostForm('Accepter', 'booking_accept', BOOKING_STATE.PENDING)
Refuse = PostForm('Refuser', 'booking_reject', BOOKING_STATE.REJECTED)
Cancel = PostForm('Annuler la location', 'booking_cancel', BOOKING_STATE.CANCELED)
Close = PostForm(u'Clôturer', 'booking_close', BOOKING_STATE.CLOSING)
Read = PostForm(u'Marquer comme lu', 'booking_read', BOOKING_STATE.PROFESSIONAL_SAW)


Incident = LinkWidget(
	url_builder=lambda request, booking: reverse(
		'booking_incident', 
		kwargs={'booking_id': booking.pk.hex}
	),
	text=u'Signaler un incident'
)

Contract = LinkWidget(
	url_builder=lambda request, booking: reverse(
		'booking_contract', 
		kwargs={'booking_id': booking.pk.hex}
	),
	text=u'Télécharger le contract de location'
)

class CommentLinkWidget(LinkWidget):
	def condition(self, request, booking):
		from django.core.exceptions import ObjectDoesNotExist
		if request.user == booking.owner:
			try:
				booking.ownercomment
			except ObjectDoesNotExist:
				return True
		else:
			try:
				booking.borrowercomment
			except ObjectDoesNotExist:
				return True
		return False

class ViewLinkWidget(LinkWidget):
	def condition(self, request, booking):
		from django.core.exceptions import ObjectDoesNotExist
		try:
			request.user == booking.owner and booking.ownercomment or booking.borrowercomment
		except ObjectDoesNotExist:
			return False
		return True

LeaveComment = CommentLinkWidget(
	url_builder=lambda request, booking: reverse(
		viewname='accounts.views.comment_booking',
		kwargs={
			'booking_id':booking.pk.hex
		}
	),
	text=u'Commenter la location',
)

SendMessageToBorrower = LinkWidget(
	url_builder=lambda request, booking: reverse(
		viewname='products.views.message_create', 
		kwargs={
			'product_id': booking.product.pk,
			'recipient_id': booking.borrower.pk
		}),
	text=u'Envoyer un message au locataire'
)

SendMessageToOwner = LinkWidget(
	url_builder=lambda request, booking: reverse(
		viewname='products.views.message_create', 
		kwargs={
			'product_id': booking.product.pk,
			'recipient_id': booking.owner.pk
		}),
	text=u'Envoyer un message au propriétaire'
)

borrower = {
    'authorizing': (Cancel, SendMessageToOwner),
    'authorized': (Cancel, SendMessageToOwner, ),
    'rejected': (SendMessageToOwner, ),
    'canceled': (), 
   	'pending': (Cancel, Contract, ),
    'ongoing': (Incident, ), 
    'ended': (Incident, LeaveComment),
    'incident': (), 
    'refunded': (),
    'deposit': (),
    'closing': (Incident, SendMessageToOwner, LeaveComment),
    'closed': (Incident, SendMessageToOwner, LeaveComment),
    'outdated': (),
    'professional': (),
    'professional_saw': (),
}

owner = {
    'authorizing': (), 
    'authorized': (Accept, Refuse, SendMessageToBorrower),
    'rejected': (),
    'canceled': (), 
   	'pending': (Contract, ),
    'ongoing': (Incident, ), 
    'ended': (Close, Incident, LeaveComment),
    'incident': (), 
    'refunded': (),
    'deposit': (),
    'closing': (Incident, SendMessageToBorrower, LeaveComment),
    'closed': (Incident, SendMessageToBorrower, LeaveComment), 
    'outdated': (),
    'professional': (Read, ),
    'professional_saw': (),
}

@register.simple_tag
def bookingaction(request, booking):
	actions = borrower if booking.borrower == request.user else owner
	possible_actions = actions[booking.state]

	return u'<ul class="action-list">{actions}</ul>'.format(
		actions=u''.join(
			[action.render(request, booking) 
				for action in possible_actions 
				if action.condition(request, booking)]
		)
	)