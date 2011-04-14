# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth import login
from django.core.urlresolvers import reverse
from django.views.generic.simple import redirect_to, direct_to_template
from django.shortcuts import get_object_or_404

from django_lean.experiments.models import GoalRecord
from django_lean.experiments.utils import WebUser

from eloue.accounts.forms import EmailAuthenticationForm
from eloue.accounts.models import Patron
from eloue.products.forms import AlertForm, ProductForm
from eloue.products.models import Product, Picture, UNIT, Alert
from eloue.wizard import GenericFormWizard


class ProductWizard(GenericFormWizard):
    def done(self, request, form_list):
        missing_form = next((form for form in form_list if getattr(form.__class__, '__name__', None) == 'MissingInformationForm'), None)
        if request.user.is_anonymous():  # Create new Patron
            auth_form = next((form for form in form_list if isinstance(form, EmailAuthenticationForm)), None)
            new_patron = auth_form.get_user()
            if not new_patron:
                new_patron = Patron.objects.create_inactive(missing_form.cleaned_data['username'],
                    auth_form.cleaned_data['email'], missing_form.cleaned_data['password1'])
                if hasattr(settings, 'AFFILIATE_TAG'):
                    # Assign affiliate tag, no need to save, since missing_form should do it for us
                    new_patron.affiliate = settings.AFFILIATE_TAG
            if not hasattr(new_patron, 'backend'):
                from django.contrib.auth import load_backend
                backend = load_backend(settings.AUTHENTICATION_BACKENDS[0])
                new_patron.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
            login(request, new_patron)
        else:
            new_patron = request.user
        
        if missing_form:
            missing_form.instance = new_patron
            new_patron, new_address, new_phone = missing_form.save()
        
        # Create product
        product_form = form_list[0]
        product_form.instance.owner = new_patron
        product_form.instance.address = new_address
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
        
        return redirect_to(request, product.get_absolute_url(), permanent=False)
    
    def get_form(self, step, data=None, files=None):
        if issubclass(self.form_list[step], ProductForm):
            if files and '0-picture' in files:  # Hack to get image working
                data['0-picture_id'] = Picture.objects.create(image=files['0-picture']).id
                del files['0-picture']
            return self.form_list[step](data, files, prefix=self.prefix_for_step(step),
                initial=self.initial.get(step, None), instance=Product(quantity=1, deposit_amount=0))
        if not issubclass(self.form_list[step], (ProductForm, EmailAuthenticationForm)):
            initial = {
                'addresses__country': settings.LANGUAGE_CODE.split('-')[1].upper(),
            }
            return self.form_list[step](data, files, prefix=self.prefix_for_step(step),
                initial=initial)
        return super(ProductWizard, self).get_form(step, data, files)
    
    def get_template(self, step):
        if issubclass(self.form_list[step], EmailAuthenticationForm):
            return 'products/product_register.html'
        elif issubclass(self.form_list[step], ProductForm):
            return 'products/product_create.html'
        else:
            return 'products/product_missing.html'
    

class AlertWizard(GenericFormWizard):
    def done(self, request, form_list):
        missing_form = next((form for form in form_list if getattr(form.__class__, '__name__', None) == 'MissingInformationForm'), None)
        
        if request.user.is_anonymous():  # Create new Patron
            auth_form = next((form for form in form_list if isinstance(form, EmailAuthenticationForm)), None)
            new_patron = auth_form.get_user()
            if not new_patron:
                new_patron = Patron.objects.create_inactive(missing_form.cleaned_data['username'],
                    auth_form.cleaned_data['email'], missing_form.cleaned_data['password1'])
                if hasattr(settings, 'AFFILIATE_TAG'):
                    # Assign affiliate tag, no need to save, since missing_form should do it for us
                    new_patron.affiliate = settings.AFFILIATE_TAG
            if not hasattr(new_patron, 'backend'):
                from django.contrib.auth import load_backend
                backend = load_backend(settings.AUTHENTICATION_BACKENDS[0])
                new_patron.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
            login(request, new_patron)
        else:
            new_patron = request.user
        
        if missing_form:
            missing_form.instance = new_patron
            new_patron, new_address, new_phone = missing_form.save()
        
        # Create and send alerts
        alert_form = form_list[0]
        alert_form.instance.patron = new_patron
        alert_form.instance.address = new_address
        alert = alert_form.save()
        
        alert.send_alerts()
        return redirect_to(request, reverse("alert_list"), permanent=False)
    
    def get_template(self, step):
        if issubclass(self.form_list[step], EmailAuthenticationForm):
            return 'products/alert_register.html'
        elif issubclass(self.form_list[step], AlertForm):
            return 'products/alert_create.html'
        else:
            return 'products/alert_missing.html'

class AlertAnswerWizard(GenericFormWizard):
    def done(self, request, form_list):
        missing_form = next((form for form in form_list if getattr(form.__class__, '__name__', None) == 'MissingInformationForm'), None)
        if request.user.is_anonymous():  # Create new Patron
            auth_form = next((form for form in form_list if isinstance(form, EmailAuthenticationForm)), None)
            new_patron = auth_form.get_user()
            if not new_patron:
                new_patron = Patron.objects.create_inactive(missing_form.cleaned_data['username'],
                    auth_form.cleaned_data['email'], missing_form.cleaned_data['password1'])
                if hasattr(settings, 'AFFILIATE_TAG'):
                    # Assign affiliate tag, no need to save, since missing_form should do it for us
                    new_patron.affiliate = settings.AFFILIATE_TAG
            if not hasattr(new_patron, 'backend'):
                from django.contrib.auth import load_backend
                backend = load_backend(settings.AUTHENTICATION_BACKENDS[0])
                new_patron.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
            login(request, new_patron)
        else:
            new_patron = request.user

        if missing_form:
            missing_form.instance = new_patron
            new_patron, new_address, new_phone = missing_form.save()

        # Create product
        product_form = form_list[0]
        product_form.instance.owner = new_patron
        product_form.instance.address = new_address
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
        
        return redirect_to(request, reverse("alert_inform_success", args=[alert.pk]), permanent=False)

    def get_form(self, step, data=None, files=None):
        if issubclass(self.form_list[step], ProductForm):
            if files and '0-picture' in files:  # Hack to get image working
                data['0-picture_id'] = Picture.objects.create(image=files['0-picture']).id
                del files['0-picture']
            return self.form_list[step](data, files, prefix=self.prefix_for_step(step),
                initial=self.initial.get(step, None), instance=Product(quantity=1, deposit_amount=0))
        if not issubclass(self.form_list[step], (ProductForm, EmailAuthenticationForm)):
            initial = {
                'addresses__country': settings.LANGUAGE_CODE.split('-')[1].upper(),
            }
            return self.form_list[step](data, files, prefix=self.prefix_for_step(step),
                initial=initial)
        return super(ProductWizard, self).get_form(step, data, files)

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
    
