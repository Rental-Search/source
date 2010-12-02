# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
import django.forms as forms
from django.test import TestCase
from django.utils.translation import ugettext as _

from eloue.accounts.forms import PatronPasswordChangeForm
from eloue.accounts.models import Patron


class PatronTest(TestCase):
    fixtures = ['patron']
    
    def test_patron_detail_view(self):
        response = self.client.get(reverse('patron_detail', args=['alexandre']))
        self.assertEqual(response.status_code, 200)
    
    def test_patron_detail_compat(self):
        response = self.client.get(reverse('patron_detail_compat', args=['alexandre', 1]))
        self.assertRedirects(response, reverse('patron_detail', args=['alexandre']), status_code=301)
    
    def test_patron_edit(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')
        response = self.client.post(reverse('patron_edit'), {
            'first_name': 'Alex',
            'last_name': 'Woog',
            'username': 'alexandre',
            'email': 'alexandre.woog@e-loue.com',
            'is_professional': False,
            'is_subscribed': False
        })
        self.assertEquals(response.status_code, 200)
        patron = Patron.objects.get(email='alexandre.woog@e-loue.com')
        self.assertEquals(patron.first_name, 'Alex')
    
    def test_patron_edit_form(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')
        response = self.client.get(reverse('patron_edit'))
        self.assertEquals(response.status_code, 200)
        self.assertTrue('form' in response.context)
        self.assertTrue(isinstance(response.context['form'], forms.ModelForm))
    
    def test_patron_edit_email_already_exists(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')
        response = self.client.post(reverse('patron_edit'), {
            'first_name': 'Alex',
            'last_name': 'Woog',
            'username': 'alexandre',
            'email': 'timothee.peignier@e-loue.com',
            'is_professional': False,
            'is_subscribed': False
        })
        self.assertEquals(response.status_code, 200)
        self.assertFormError(response, 'form', 'email', _(u"Un compte avec cet email existe déjà"))
    
    def test_patron_edit_email_empty(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')
        response = self.client.post(reverse('patron_edit'), {
            'first_name': 'Alex',
            'last_name': 'Woog',
            'email': '',
            'username': 'alexandre',
            'is_professional': False,
            'is_subscribed': False
        })
        self.assertEquals(response.status_code, 200)
        self.assertFormError(response, 'form', 'email', _(u"This field is required."))
    
    def test_patron_edit_junk_email(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')
        response = self.client.post(reverse('patron_edit'), {
            'first_name': 'Alex',
            'last_name': 'Woog',
            'username': 'alexandre',
            'email': 'alexandre.woog@jetable.net',
            'is_professional': False,
            'is_subscribed': False
        })
        self.assertEquals(response.status_code, 200)
        self.assertFormError(response, 'form', 'email', _(u"Pour garantir un service de qualité et la sécurité des utilisateurs de Croisé dans le métro, vous ne pouvez pas vous enregistrer avec une adresse email jetable. Ne craignez rien, vous ne recevrez aucun courrier indésirable."))
    
    def test_patron_password_form(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')
        response = self.client.get(reverse('patron_edit_password'))
        self.assertEquals(response.status_code, 200)
        self.assertTrue('form' in response.context)
        self.assertTrue(isinstance(response.context['form'], PatronPasswordChangeForm))
    
    def test_patron_password(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')
        response = self.client.post(reverse('patron_edit_password'), {
            'old_password': 'alexandre',
            'new_password1': 'alex',
            'new_password2': 'alex'
        })
        self.assertEquals(response.status_code, 200)
    
    def test_patron_dashboard(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')
        response = self.client.get(reverse('dashboard'))
        self.assertEquals(response.status_code, 200)
    
