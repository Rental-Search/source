# -*- coding: utf-8 -*-
from mock import patch
from urllib import urlencode
from urlparse import urlsplit

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import QueryDict
from django.test import TestCase
from django.utils.translation import ugettext as _

from eloue.wizard import MultiPartFormWizard
from eloue.accounts.models import Patron, Avatar, FacebookSession

class AccountWizardTest(TestCase):
    fixtures = ['patron']
    
    def test_zero_step(self):
        response = self.client.get(reverse('auth_login'))
        self.assertEquals(response.status_code, 200)
    
    def test_first_step_with_existing_account(self):
        response = self.client.post(reverse('auth_login'), {
            '0-email': 'alexandre.woog@e-loue.com',
            '0-exists': 1,
            '0-password': 'alexandre',
            'wizard_step': 0
        })
        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL, status_code=302)
        
        scheme, netloc, path, query, fragment = urlsplit(response['Location'])
        redirect_response = response.client.get(path, QueryDict(query))
        self.assertTrue(redirect_response.context['user'].is_authenticated())
    
    def test_first_step_with_redirect(self):
        args = urlencode({'next': reverse('auth_login')})
        response = self.client.post("%s?%s" % (reverse('auth_login'), args), {
            '0-email': 'alexandre.woog@e-loue.com',
            '0-exists': 1,
            '0-password': 'alexandre',
            'wizard_step': 0
        })
        self.assertRedirects(response, reverse('auth_login'), status_code=302)
        scheme, netloc, path, query, fragment = urlsplit(response['Location'])
        redirect_response = response.client.get(path, QueryDict(query))
        self.assertTrue(redirect_response.context['user'].is_authenticated())
    
    def test_first_step_with_inactive_account(self):
        response = self.client.post(reverse('auth_login'), {
            '0-email': 'benjamin.marchandlenoir@e-loue.com',
            '0-exists': 1,
            '0-password': 'benjamin',
            'wizard_step': 0
        })
        self.assertTrue(response.status_code, 200)
        self.assertFormError(response, 'form', None, _(u"Ce compte est inactif parce qu'il n'a pas été activé."))
    
    def test_first_step_with_wrong_password(self):
        response = self.client.post(reverse('auth_login'), {
            '0-email': 'alexandre.woog@e-loue.com',
            '0-exists': 1,
            '0-password': 'erdnaxela',
            'wizard_step': 0
        })
        self.assertTrue(response.status_code, 200)
        self.assertFormError(response, 'form', None, _(u"Veuillez saisir une adresse email et un mot de passe valide."))
    
    def test_first_step_with_wrong_email(self):
        response = self.client.post(reverse('auth_login'), {
            '0-email': 'alexandre@e-loue.com',
            '0-exists': 1,
            '0-password': 'alexandre',
            'wizard_step': 0
        })
        self.assertTrue(response.status_code, 200)
        self.assertFormError(response, 'form', None, _(u"Veuillez saisir une adresse email et un mot de passe valide."))
     
    def test_first_step_with_blacklisted_email(self):
        response = self.client.post(reverse('auth_login'), {
            '0-email': 'alexandre.woog@jetable.org',
            '0-exists': 1,
            '0-password': 'alexandre',
            'wizard_step': 0
        })
        self.assertTrue(response.status_code, 200)
        self.assertFormError(response, 'form', 'email', _(u"Pour garantir un service de qualité et la sécurité des utilisateurs de e-loue.com, vous ne pouvez pas vous enregistrer avec une adresse email jetable."))
    
    def test_first_step_with_already_existing_account(self):
        response = self.client.post(reverse('auth_login'), {
            '0-email': 'alexandre.woog@e-loue.com',
            '0-exists': 0,
            'wizard_step': 0
        })
        self.assertTrue(response.status_code, 200)
        self.assertFormError(response, 'form', 'email', _(u"Un compte existe déjà pour cet email"))
    
    def test_first_step_without_account(self):
        response = self.client.post(reverse('auth_login'), {
            '0-email': 'hocus.pocus@e-loue.com',
            '0-exists': 0,
            'wizard_step': 0
        })
        self.assertTrue(response.status_code, 200)
        self.assertContains(response, "1-username")
    
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_second_step(self, mock_return):
        mock_return.return_value = 'b5d8e7ffcc52f852c688983ecb30ead6'
        response = self.client.post(reverse('auth_login'), {
            '1-username': 'hocus-pocus',
            '1-password1': 'sucop',
            '1-password2': 'sucop',
            'wizard_step': 1,
            '0-email': 'hocus.pocus@e-loue.com',
            '0-exists': 0,
            '0-password': '',
            'hash_0': 'b5d8e7ffcc52f852c688983ecb30ead6'
        })
        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL, status_code=302)
        
        scheme, netloc, path, query, fragment = urlsplit(response['Location'])
        redirect_response = response.client.get(path, QueryDict(query))
        self.assertTrue(redirect_response.context['user'].is_authenticated())
        self.assertTrue(not redirect_response.context['user'].is_active)
    
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_second_step_with_existing_username(self, mock_return):
        mock_return.return_value = 'b5d8e7ffcc52f852c688983ecb30ead6'
        response = self.client.post(reverse('auth_login'), {
            '1-username': 'alexandre',
            '1-password1': 'sucop',
            '1-password2': 'sucop',
            'wizard_step': 1,
            '0-email': 'hocus.pocus@e-loue.com',
            '0-exists': 0,
            '0-password': '',
            'hash_0': 'b5d8e7ffcc52f852c688983ecb30ead6'
        })
        self.assertTrue(response.status_code, 200)
        self.assertFormError(response, 'form', 'username', _(u"Ce nom d'utilisateur est déjà pris."))
    
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_second_step_with_mismatching_password(self, mock_return):
        mock_return.return_value = 'b5d8e7ffcc52f852c688983ecb30ead6'
        response = self.client.post(reverse('auth_login'), {
            '1-username': 'hocus-pocus',
            '1-password1': 'sucop',
            '1-password2': 'pocus',
            'wizard_step': 1,
            '0-email': 'hocus.pocus@e-loue.com',
            '0-exists': 0,
            '0-password': '',
            'hash_0': 'b5d8e7ffcc52f852c688983ecb30ead6'
        })
        self.assertTrue(response.status_code, 200)
        self.assertFormError(response, 'form', 'password2', _(u"Vos mots de passe ne correspondent pas"))
    

class FacebookAccountWizardTest(TestCase):
    fixtures = ['patron', 'facebooksession']
    
    def test_zero_step(self):
        response = self.client.get(reverse('auth_login'))
        self.assertEquals(response.status_code, 200)
    
    def test_first_step_with_existing_account(self):
        response = self.client.post(reverse('auth_login'), {
            '0-email': '',
            '0-exists': 1,
            '0-password': '',
            'wizard_step': 0,
            '0-facebook_access_token': 'AAAC0EJC00lQBAOf7XANWgcw2UzKdLn5q13bUp07KRPy8MntAdsPzJsnFOiCu7ZCegQIX46eu7OAjXp3sFucTCRKYGH42OW9ywcissIAZDZD',
            '0-facebook_expires': '0',
            '0-facebook_uid': '100003207275288'
        })
        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL, status_code=302)
        
        scheme, netloc, path, query, fragment = urlsplit(response['Location'])
        redirect_response = response.client.get(path, QueryDict(query))
        self.assertTrue(redirect_response.context['user'].is_authenticated())
    
    def test_first_step_with_existing_account_with_exist0(self):
        response = self.client.post(reverse('auth_login'), {
            '0-email': '',
            '0-exists': 0,
            '0-password': '',
            'wizard_step': 0,
            '0-facebook_access_token': 'AAAC0EJC00lQBAOf7XANWgcw2UzKdLn5q13bUp07KRPy8MntAdsPzJsnFOiCu7ZCegQIX46eu7OAjXp3sFucTCRKYGH42OW9ywcissIAZDZD',
            '0-facebook_expires': '0',
            '0-facebook_uid': '100003207275288'
        })
        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL, status_code=302)
        
        scheme, netloc, path, query, fragment = urlsplit(response['Location'])
        redirect_response = response.client.get(path, QueryDict(query))
        self.assertTrue(redirect_response.context['user'].is_authenticated())

    def test_first_step_with_redirect(self):
        args = urlencode({'next': reverse('auth_login')})
        response = self.client.post("%s?%s" % (reverse('auth_login'), args), {
            '0-email': '',
            '0-exists': 0,
            '0-password': '',
            'wizard_step': 0,
            '0-facebook_access_token': 'AAAC0EJC00lQBAOf7XANWgcw2UzKdLn5q13bUp07KRPy8MntAdsPzJsnFOiCu7ZCegQIX46eu7OAjXp3sFucTCRKYGH42OW9ywcissIAZDZD',
            '0-facebook_expires': '0',
            '0-facebook_uid': '100003207275288'
        })
        self.assertRedirects(response, reverse('auth_login'), status_code=302)
        scheme, netloc, path, query, fragment = urlsplit(response['Location'])
        redirect_response = response.client.get(path, QueryDict(query))
        self.assertTrue(redirect_response.context['user'].is_authenticated())
    
    def test_first_step_without_account(self):
        response = self.client.post(reverse('auth_login'), {
                    '0-email': '',
                    '0-exists': 0,
                    '0-password': '',
                    'wizard_step': 0,
                    '0-facebook_access_token': 'AAAC0EJC00lQBAGnc6FW8QlB5tz4ppuSXeR0FQ8kdCagwHwRraHDBI4HE7eigTprugjh0uGPu4h2FG2VEaRO8RxRcm8ObicNyZB21JGgZDZD',
                    '0-facebook_expires': '0',
                    '0-facebook_uid': '100000609837182'
                })
        self.assertTrue(response.status_code, 200)
        self.assertContains(response, "1-username")


    
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_second_step_without_account(self, mock_return):
        mock_return.return_value = 'b5d8e7ffcc52f852c688983ecb30ead6'
        access_token = 'AAAC0EJC00lQBAGnc6FW8QlB5tz4ppuSXeR0FQ8kdCagwHwRraHDBI4HE7\
          eigTprugjh0uGPu4h2FG2VEaRO8RxRcm8ObicNyZB21JGgZDZD'
        response = self.client.post(reverse('auth_login'), {
                    '0-email': '',
                    '0-exists': 0,
                    '0-password': '',
                    'wizard_step': 1,
                    '0-facebook_access_token': access_token,
                    '0-facebook_expires': '0',
                    '0-facebook_uid': '100000609837182',
                    '1-username': 'kosii1',
                    'email': 'kosii.spam@gmail.com',
                    'hash_0': 'b5d8e7ffcc52f852c688983ecb30ead6'
                })
        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL)
        p = Patron.objects.get(username='kosii1')
        with self.assertRaises(Avatar.DoesNotExist):
            p.avatar
        self.assertEqual(p.email, 'kosii.spam@gmail.com')
        self.assertEqual(p, FacebookSession.objects.get(access_token=access_token).user)
    

    
    def test_first_step_with_wrong_password(self):
        response = self.client.post(reverse('auth_login'), {
            '0-email': 'alexandre.woog@e-loue.com',
            '0-exists': 1,
            '0-password': 'erdnaxela',
            'wizard_step': 0
        })
        self.assertTrue(response.status_code, 200)
        self.assertFormError(response, 'form', None, _(u"Veuillez saisir une adresse email et un mot de passe valide."))
    
    def test_first_step_with_wrong_email(self):
        response = self.client.post(reverse('auth_login'), {
            '0-email': 'alexandre@e-loue.com',
            '0-exists': 1,
            '0-password': 'alexandre',
            'wizard_step': 0
        })
        self.assertTrue(response.status_code, 200)
        self.assertFormError(response, 'form', None, _(u"Veuillez saisir une adresse email et un mot de passe valide."))
     
    def test_first_step_with_blacklisted_email(self):
        response = self.client.post(reverse('auth_login'), {
            '0-email': 'alexandre.woog@jetable.org',
            '0-exists': 1,
            '0-password': 'alexandre',
            'wizard_step': 0
        })
        self.assertTrue(response.status_code, 200)
        self.assertFormError(response, 'form', 'email', _(u"Pour garantir un service de qualité et la sécurité des utilisateurs de e-loue.com, vous ne pouvez pas vous enregistrer avec une adresse email jetable."))
    
    def test_first_step_with_already_existing_account(self):
        response = self.client.post(reverse('auth_login'), {
            '0-email': 'alexandre.woog@e-loue.com',
            '0-exists': 0,
            'wizard_step': 0
        })
        self.assertTrue(response.status_code, 200)
        self.assertFormError(response, 'form', 'email', _(u"Un compte existe déjà pour cet email"))
    
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_second_step(self, mock_return):
        mock_return.return_value = 'b5d8e7ffcc52f852c688983ecb30ead6'
        response = self.client.post(reverse('auth_login'), {
            '1-username': 'hocus-pocus',
            '1-password1': 'sucop',
            '1-password2': 'sucop',
            'wizard_step': 1,
            '0-email': 'hocus.pocus@e-loue.com',
            '0-exists': 0,
            '0-password': '',
            'hash_0': 'b5d8e7ffcc52f852c688983ecb30ead6'
        })
        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL, status_code=302)
        
        scheme, netloc, path, query, fragment = urlsplit(response['Location'])
        redirect_response = response.client.get(path, QueryDict(query))
        self.assertTrue(redirect_response.context['user'].is_authenticated())
        self.assertTrue(not redirect_response.context['user'].is_active)
    
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_second_step_with_existing_username(self, mock_return):
        mock_return.return_value = 'b5d8e7ffcc52f852c688983ecb30ead6'
        response = self.client.post(reverse('auth_login'), {
            '1-username': 'alexandre',
            '1-password1': 'sucop',
            '1-password2': 'sucop',
            'wizard_step': 1,
            '0-email': 'hocus.pocus@e-loue.com',
            '0-exists': 0,
            '0-password': '',
            'hash_0': 'b5d8e7ffcc52f852c688983ecb30ead6'
        })
        self.assertTrue(response.status_code, 200)
        self.assertFormError(response, 'form', 'username', _(u"Ce nom d'utilisateur est déjà pris."))
    
    @patch.object(MultiPartFormWizard, 'security_hash')
    def test_second_step_with_mismatching_password(self, mock_return):
        mock_return.return_value = 'b5d8e7ffcc52f852c688983ecb30ead6'
        response = self.client.post(reverse('auth_login'), {
            '1-username': 'hocus-pocus',
            '1-password1': 'sucop',
            '1-password2': 'pocus',
            'wizard_step': 1,
            '0-email': 'hocus.pocus@e-loue.com',
            '0-exists': 0,
            '0-password': '',
            'hash_0': 'b5d8e7ffcc52f852c688983ecb30ead6'
        })
        self.assertTrue(response.status_code, 200)
        self.assertFormError(response, 'form', 'password2', _(u"Vos mots de passe ne correspondent pas"))
    

