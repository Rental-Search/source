# -*- coding: utf-8 -*-
from django.contrib.auth.backends import ModelBackend
from django.contrib.sites.models import Site
from eloue.accounts.models import Patron


class PatronModelBackend(ModelBackend):
    def authenticate(self, username=None, password=None):
        try:
            user = Patron.objects.get(email=username)
            if user.check_password(password):
                return user
        except Patron.DoesNotExist:
            return None
    
    def get_user(self, user_id):
        try:
            return Patron.objects.get(pk=user_id)
        except Patron.DoesNotExist:
            return None

class PrivatePatronModelBackend(ModelBackend):
	def authenticate(self, username=None, password=None):
		try:
			current_site = Site.objects.get_current()
			user = Patron.objects.get(email=username, sites=current_site)
			if user.check_password(password):
				return user
		except Patron.DoesNotExist:
			return None

	def get_user(self, user_id):
		current_site = Site.objects.get_current()
		try:
			return Patron.objects.get(pk=user_id, sites=current_site)
		except Patron.DoesNotExist:
			return None
    
