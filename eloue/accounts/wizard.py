# -*- coding: utf-8 -*-
import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
from django.shortcuts import redirect

from django_lean.experiments.models import GoalRecord
from django_lean.experiments.utils import WebUser

from accounts.forms import EmailAuthenticationForm, SubscriptionEditForm
from accounts.models import Patron, Avatar, ProPackage, Subscription

from eloue.wizard import MultiPartFormWizard

class AuthenticationWizard(MultiPartFormWizard):
    def __init__(self, *args, **kwargs):
        super(AuthenticationWizard, self).__init__(*args, **kwargs)
        self.required_fields = ['username', 'password1', 'password2', 'is_professional', 'company_name', 'avatar']
        self.title = _(u'S\'incrire ou se connecter')

    def __call__(self, request, *args, **kwargs):
        self.request = request
        import oauth2 as oauth
        import urllib, urlparse, simplejson, pprint
        from django.core.urlresolvers import reverse
        scope = '["namePerson/friendly","namePerson","contact/postalAddress/home","contact/email","namePerson/last","namePerson/first"]'

        consumer_key = settings.IDN_CONSUMER_KEY
        consumer_secret = settings.IDN_CONSUMER_SECRET
        base_url = settings.IDN_BASE_URL
        return_url = settings.IDN_RETURN_URL

        request_token_url = base_url + 'oauth/requestToken'
        authorize_url = base_url + 'oauth/authorize'
        access_token_url = base_url + 'oauth/accessToken'
        me_url = base_url + 'anywhere/me?oauth_scope=%s' % (scope, )
        consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)
        client = oauth.Client(consumer)
        if request.method == 'GET':
            if request.GET.get('connected'):
                response, content = client.request(request_token_url, "GET")
                request_token = dict(urlparse.parse_qsl(content))
                request.session['request_token'] = request_token
                link = "%s?oauth_token=%s&oauth_callback=%s&oauth_scope=%s" % (
                    authorize_url, 
                    request_token['oauth_token'], 
                    return_url, 
                    scope
                )
                return redirect(link)
            elif request.GET.get('oauth_verifier'):
                idn_oauth_verifier = request.GET.get('oauth_verifier')
                request_token = oauth.Token(
                    request.session['request_token']['oauth_token'],
                    request.session['request_token']['oauth_token_secret'])
                request_token.set_verifier(idn_oauth_verifier)
                client = oauth.Client(consumer, request_token)
                response, content = client.request(access_token_url, "GET")
                assert simplejson.loads(response['status']) == 200
                access_token_data = dict(urlparse.parse_qsl(content))
                access_token = oauth.Token(access_token_data['oauth_token'],
                    access_token_data['oauth_token_secret'])
                client = oauth.Client(consumer, access_token)
                response, content = client.request(me_url, "GET")
                assert simplejson.loads(response['status']) == 200
                content = simplejson.loads(content)
                idn_id = content['id']
                request.session['idn_info'] = {
                    'access_token': access_token_data['oauth_token'],
                    'idn_id': idn_id
                }
                request.session[(idn_id, access_token_data['oauth_token'])] = access_token_data
                del request.session['request_token']
                return redirect('auth_login')
            elif 'idn_info' in request.session:
                self.initial[0] = {
                    'idn_id': request.session['idn_info']['idn_id'],
                    'idn_access_token': request.session['idn_info']['access_token']
                }

        return super(AuthenticationWizard, self).__call__(request, *args, **kwargs)

    def get_form(self, step, data=None, files=None):
        form = super(AuthenticationWizard, self).get_form(step, data, files)
        form.request = self.request
        return form

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
        from django.db.models import Q
        now = datetime.datetime.now()
        plans = ProPackage.objects.filter(
            Q(valid_until__isnull=True, valid_from__lte=now) |
            Q(valid_until__isnull=False, valid_until__gte=now)).order_by('maximum_items')

        self.extra_context.update({'plans': plans})
        return super(ProSubscriptionWizard, self).__call__(request, *args, **kwargs)

    def done(self, request, form_list):
        super(ProSubscriptionWizard, self).done(request, form_list)
        request.user.is_professional = True
        request.user.save()
        subscription_form = form_list[0]
        subscription_form.is_valid()
        propackage = subscription_form.cleaned_data['subscription']
        if propackage.maximum_items is None or request.user.products.count() < propackage.maximum_items:
            current_subscription = request.user.current_subscription
            request.user.subscribe(propackage)
            if current_subscription:
                messages.success(request, _(u'Vous avez changer d\'abonnement avec succès'))
            else:
                messages.success(request, _(u'Votre inscription à l\'abonnement est validé'))
        else:
            messages.error(request, _(u'Votre nombre d\'annonces dépasse le nombre d\'annonce maximum de cet abonnement. Merci de choisir un abonnement plus important'))
        return redirect('patron_edit_subscription')

    def get_template(self, step):
        if issubclass(self.form_list[step], SubscriptionEditForm):
            return 'accounts/patron_subscription.html'
        return super(ProSubscriptionWizard, self).get_template(step)

    def process_step(self, request, form, step):
        super(ProSubscriptionWizard, self).process_step(request, form, step)
        self.extra_context.setdefault('preview', {}).update(form.cleaned_data)

