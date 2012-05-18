# -*- coding: utf-8 -*-
from django_lean.experiments.models import GoalRecord
from django_lean.experiments.utils import WebUser

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import ugettext as _
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic.simple import direct_to_template, redirect_to

from eloue.wizard import MultiPartFormWizard
from eloue.accounts.forms import EmailAuthenticationForm, make_missing_data_form
from eloue.accounts.models import Patron, Avatar
from eloue.products.forms import AlertForm, ProductForm, MessageEditForm
from eloue.products.models import Product, Picture, UNIT, Alert


class ProductWizard(MultiPartFormWizard):

    def __init__(self, *args, **kwargs):
        super(ProductWizard, self).__init__(*args, **kwargs)
        self.title = _(u'Ajouter une annonce')

    def done(self, request, form_list):
        super(ProductWizard, self).done(request, form_list)

        # Create product
        product_form = form_list[0]
        product_form.instance.owner = self.new_patron
        product_form.instance.address = self.new_address
        product = product_form.save()
        
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
        
        messages.success(request, _(u"Votre objet a bien été ajouté"))
        GoalRecord.record('new_object', WebUser(request))
        return redirect_to(request, product.get_absolute_url(), permanent=False)
    
    def get_form(self, step, data=None, files=None):
        next_form = self.form_list[step]
        if issubclass(next_form, ProductForm):
            if files and '0-picture' in files:  # Hack to get image working
                data['0-picture_id'] = Picture.objects.create(image=files['0-picture']).id
                del files['0-picture']
            return next_form(
                data, files, prefix=self.prefix_for_step(step),
                initial=self.initial.get(step, None), instance=next_form._meta.model(quantity=1, deposit_amount=0))
        return super(ProductWizard, self).get_form(step, data, files)
    
    def get_template(self, step):
        if issubclass(self.form_list[step], EmailAuthenticationForm):
            return 'accounts/auth_login.html'
        elif issubclass(self.form_list[step], ProductForm):
            return 'products/product_create.html'
        else:
            return 'accounts/auth_missing.html'

            
class MessageWizard(MultiPartFormWizard):
    
    def __init__(self, *args, **kwargs):
        super(MessageWizard, self).__init__(*args, **kwargs)
        self.required_fields = ['username', 'password1', 'password2', 'avatar']
        self.title = _(u'Envoyer un message')
    
    def __call__(self, request, product_id, recipient_id, *args, **kwargs):
        product = get_object_or_404(Product, pk=product_id) if product_id is not None else None
        recipient = get_object_or_404(Patron, pk=recipient_id)
        self.extra_context.update({'product': product})
        self.extra_context.update({'recipient': recipient})
        return super(MessageWizard, self).__call__(request, *args, **kwargs)
        
    def done(self, request, form_list):
        super(MessageWizard, self).done(request, form_list)
        # Create message
        product = self.extra_context["product"]
        recipient = self.extra_context["recipient"]
        if self.new_patron == recipient:
            messages.error(request, _(u"Vous ne pouvez pas vous envoyer des messages."))
            try:
                return redirect(product.get_absolute_url())
            except AttributeError:
                return redirect(request.user.get_absolute_url())
        else:
            message_form = form_list[0]
            message = message_form.save(product=product, sender=self.new_patron, recipient=recipient)
            messages.success(request, _(u"Votre message a bien été envoyé au propriétaire"))
            return redirect('thread_details', thread_id=message[0].productrelatedmessage.thread.id)

    def get_template(self, step):
        if issubclass(self.form_list[step], EmailAuthenticationForm):
            return 'accounts/auth_login.html'
        elif issubclass(self.form_list[step], MessageEditForm):
            return 'django_messages/message_create.html'
        else:
            return 'accounts/auth_missing.html'

    
class AlertWizard(MultiPartFormWizard):
    def done(self, request, form_list):
        super(AlertWizard, self).done(request, form_list)
        # Create and send alerts
        alert_form = form_list[0]
        alert_form.instance.patron = self.new_patron
        alert_form.instance.address = self.new_address
        alert = alert_form.save()

        if not settings.AUTHENTICATION_BACKENDS[0] == 'eloue.accounts.auth.PrivatePatronModelBackend':
            alert.send_alerts()

        messages.success(request, _(u"Votre alerte a bien été créée"))
        return redirect_to(request, reverse("alert_edit"), permanent=False)

    def get_template(self, step):
        if issubclass(self.form_list[step], EmailAuthenticationForm):
            return 'products/alert_register.html'
        elif issubclass(self.form_list[step], AlertForm):
            return 'products/alert_create.html'
        else:
            return 'products/alert_missing.html'

    
class AlertAnswerWizard(MultiPartFormWizard):
    def done(self, request, form_list):
        super(AlertAnswerWizard, self).done(request, form_list)
        # Create product
        product_form = form_list[0]
        product_form.instance.owner = self.new_patron
        product_form.instance.address = self.new_address
        product = product_form.save()

        for unit in UNIT.keys():
            field = "%s_price" % unit.lower()
            if field in product_form.cleaned_data and product_form.cleaned_data[field]:
                product.prices.create(
                    unit=UNIT[unit],
                    amount=product_form.cleaned_data[field]
                )

        if product_form.cleaned_data.get('picture_id', None):
            product.pictures.add(Picture.objects.get(pk=product_form.cleaned_data['picture_id']))

        GoalRecord.record('new_object', WebUser(request))

        alert = self.extra_context['alert']
        alert.send_alerts_answer(product)
        
        return redirect_to(request, reverse("alert_inform_success", args=[alert.pk]), permanent=False)

    def get_form(self, step, data=None, files=None):
        if issubclass(self.form_list[step], ProductForm):
            if files and '0-picture' in files:  # Hack to get image working
                data['0-picture_id'] = Picture.objects.create(image=files['0-picture']).id
                del files['0-picture']
            return self.form_list[step](data, files, prefix=self.prefix_for_step(step),
                initial=self.initial.get(step, None), instance=Product(quantity=1, deposit_amount=0))
        return super(AlertAnswerWizard, self).get_form(step, data, files)

    def parse_params(self, request, *args, **kwargs):
        alert = get_object_or_404(Alert, pk=kwargs["alert_id"])
        self.extra_context['alert'] = alert

    def get_template(self, step):
        if issubclass(self.form_list[step], EmailAuthenticationForm):
            return 'products/product_register.html'
        elif issubclass(self.form_list[step], ProductForm):
            return 'products/product_create.html'
        else:
            return 'products/product_missing.html'
            
        
