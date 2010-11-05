# -*- coding: utf-8 -*-
from urlparse import urlsplit

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import QueryDict
from django.test import TestCase
from django.utils.translation import ugettext as _

class AccountWizardTest(TestCase):
    fixtures = ['patron']
    
    def setUp(self):
        self.old_secret_key = settings.SECRET_KEY
        settings.SECRET_KEY = "123"
    
    def test_zero_step(self):
        response = self.client.get(reverse('auth_login'))
        self.assertEquals(response.status_code, 200)
    
    def test_first_step_with_existing_account(self):
        response = self.client.post(reverse('auth_login'), {
            '0-email':'alexandre.woog@e-loue.com',
            '0-exists':1,
            '0-password':'alexandre',
            'wizard_step':0
        })
        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL, status_code=301)
        
        scheme, netloc, path, query, fragment = urlsplit(response['Location'])
        redirect_response = response.client.get(path, QueryDict(query))
        self.assertTrue(redirect_response.context['user'].is_authenticated())
    
    def test_first_step_with_inactive_account(self):
        response = self.client.post(reverse('auth_login'), {
            '0-email':'benjamin.marchandlenoir@e-loue.com',
            '0-exists':1,
            '0-password':'benjamin',
            'wizard_step':0
        })
        self.assertTrue(response.status_code, 200)
        self.assertFormError(response, 'form', None, _(u"Ce compte est inactif parce qu'il n'a pas été activé."))
    
    def test_first_step_with_wrong_password(self):
        response = self.client.post(reverse('auth_login'), {
            '0-email':'alexandre.woog@e-loue.com',
            '0-exists':1,
            '0-password':'erdnaxela',
            'wizard_step':0
        })
        self.assertTrue(response.status_code, 200)
        self.assertFormError(response, 'form', None, _(u"Veuillez saisir une adresse email et un mot de passe valide."))
    
    def test_first_step_with_wrong_email(self):
        response = self.client.post(reverse('auth_login'), {
            '0-email':'alexandre@e-loue.com',
            '0-exists':1,
            '0-password':'alexandre',
            'wizard_step':0
        })
        self.assertTrue(response.status_code, 200)
        self.assertFormError(response, 'form', None, _(u"Veuillez saisir une adresse email et un mot de passe valide."))
     
    def test_first_step_with_blacklisted_email(self):
        response = self.client.post(reverse('auth_login'), {
            '0-email':'alexandre.woog@jetable.org',
            '0-exists':1,
            '0-password':'alexandre',
            'wizard_step':0
        })
        self.assertTrue(response.status_code, 200)
        self.assertFormError(response, 'form', 'email', _(u"Pour garantir un service de qualité et la sécurité des utilisateurs de e-loue.com, vous ne pouvez pas vous enregistrer avec une adresse email jetable."))
    
    def test_first_step_with_already_existing_account(self):
        response = self.client.post(reverse('auth_login'), {
            '0-email':'alexandre.woog@e-loue.com',
            '0-exists':0,
            'wizard_step':0
        })
        self.assertTrue(response.status_code, 200)
        self.assertFormError(response, 'form', 'email', _(u"Un compte existe déjà pour cet email"))
    
    def test_first_step_without_account(self):
        response = self.client.post(reverse('auth_login'), {
            '0-email':'hocus.pocus@e-loue.com',
            '0-exists':0,
            'wizard_step':0
        })
        self.assertTrue(response.status_code, 200)
        self.assertContains(response, "Pseudo")
    
    def tearDown(self):
        settings.SECRET_KEY = self.old_secret_key
    
