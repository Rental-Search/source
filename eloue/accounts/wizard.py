# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
from django.shortcuts import redirect

from django_lean.experiments.models import GoalRecord
from django_lean.experiments.utils import WebUser

from eloue.accounts.forms import EmailAuthenticationForm, make_missing_data_form
from eloue.accounts.models import Patron, Avatar
from eloue.wizard import MultiPartFormWizard

class AuthenticationWizard(MultiPartFormWizard):

    def __init__(self, *args, **kwargs):
        super(AuthenticationWizard, self).__init__(*args, **kwargs)
        self.required_fields = ['username', 'password1', 'password2', 'is_professional', 'company_name', 'avatar']
        self.title = _(u'S\'incrire ou se connecter')

    def done(self, request, form_list):
        super(AuthenticationWizard, self).done(request, form_list)
        if request.user.is_active:
            GoalRecord.record('authentication', WebUser(request))
            messages.success(request, _(u"Bienvenue !"))
        else:
            GoalRecord.record('registration', WebUser(request))
            messages.info(request, _(u"Bienvenue ! Nous vous avons envoyé un lien de validation par email. Cette validation est impérative pour terminer votre enregistrement."))
        return redirect(self.redirect_path, permanent=False)
    
    def parse_params(self, request, *args, **kwargs):
        redirect_path = request.REQUEST.get('next', '')
        if not redirect_path or '//' in redirect_path or ' ' in redirect_path:
            self.redirect_path = settings.LOGIN_REDIRECT_URL
        else:
            self.redirect_path = redirect_path
        
    def get_template(self, step):
        if issubclass(self.form_list[step], EmailAuthenticationForm):
            return 'accounts/auth_login.html'
        else:
            return 'accounts/auth_missing.html'
    
class ProSubscriptionWizard(AuthenticationWizard):
    def __init__(self, *args, **kwargs):
        super(ProSubscriptionWizard, self).__init__(*args, **kwargs)
        self.required_fields += ['cvv', 'holder_name', 'card_number', 'expires']

    def __call__(self, request, *args, **kwargs):
        import datetime
        from eloue.accounts.models import ProPackage
        from django.db.models import Q
        now = datetime.datetime.now()
        plans = ProPackage.objects.filter(
            Q(valid_until__isnull=True, valid_from__lte=now) |
            Q(valid_until__isnull=False, valid_until__gte=now)).order_by('maximum_items')

        self.extra_context.update({'plans': plans})
        return super(ProSubscriptionWizard, self).__call__(request, *args, **kwargs)

    def done(self, request, form_list):
        super(ProSubscriptionWizard, self).done(request, form_list)
        from eloue.accounts.models import ProPackage, Subscription
        subscription_form = form_list[0]
        subscription_form.is_valid()
        propackage = subscription_form.cleaned_data['subscription']
        if request.user.products.count() <= propackage.maximum_items:
            current_subscription = request.user.current_subscription
            if current_subscription:
                current_subscription.subscription_ended = datetime.datetime.now()
            Subscription.objects.create(patron=request.user, propackage=propackage)
            if current_subscription:
                messages.success(request, 'You have successfully changed your plan')
            else:
                messages.success(request, 'You have successfuly subscribed to Eloue pro')
        else:
            messages.error(request, 'RRRRR')
        return redirect('patron_edit_subscription')

    def get_template(self, step):
        from eloue.accounts.forms import SubscriptionEditForm
        if issubclass(self.form_list[step], SubscriptionEditForm):
            return 'accounts/patron_subscription.html'
        return super(ProSubscriptionWizard, self).get_template(step)
