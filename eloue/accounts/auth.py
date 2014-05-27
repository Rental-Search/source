# -*- coding: utf-8 -*-
import hashlib

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import BasePasswordHasher, mask_hash
from django.contrib.sites.models import Site
from django.utils.datastructures import SortedDict
from django.utils.crypto import (
    pbkdf2, constant_time_compare, get_random_string)
from django.utils.translation import ugettext_noop as _
from accounts.models import Patron


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
	

class MD5PasswordHasher(BasePasswordHasher):
    """
    The Salted MD5 password hashing algorithm (not recommended)
    """
    algorithm = "md5"

    def encode(self, password, salt):
        hash = hashlib.md5(salt + password).hexdigest()
        return "%s$%s$%s" % (self.algorithm, salt, hash)

    def verify(self, password, encoded):
        algorithm, salt, hash = encoded.split('$', 2)
        assert algorithm == self.algorithm
        encoded_2 = self.encode(password, salt)
        return constant_time_compare(encoded, encoded_2)

    def safe_summary(self, encoded):
        algorithm, salt, hash = encoded.split('$', 2)
        assert algorithm == self.algorithm
        return SortedDict([
            (_('algorithm'), algorithm),
            (_('salt'), mask_hash(salt, show=2)),
            (_('hash'), mask_hash(hash)),
        ])
