# -*- coding: utf-8 -*-
import hashlib
import random
import re
import datetime

from django.contrib.auth.models import UserManager
from django.contrib.gis.db.models import GeoManager
from django.db.models import Q

SHA1_RE = re.compile('^[a-f0-9]{40}$')


class PatronManager(UserManager, GeoManager):
    def exists(self, **kwargs):
        try:
            self.get(**kwargs)
            return True
        except self.model.DoesNotExist:
            return False
    
    def activate(self, activation_key):
        """
        Validate an activation key and activate the corresponding
        ``Patron`` if valid.
        
        If the key is valid and has not expired, return the ``Patron``
        after activating.
        
        If the key is not valid or has expired, return ``False``.
        
        If the key is valid but the ``Patron`` is already active,
        return ``False``.
        
        To prevent reactivation of an account which has been
        deactivated by site administrators, the activation key is
        reset to None after successful activation.
        """
        # Make sure the key we're trying conforms to the pattern of a
        # SHA1 hash; if it doesn't, no point trying to look it up in
        # the database.
        if SHA1_RE.search(activation_key):
            try:
                patron = self.get(activation_key=activation_key)
            except self.model.DoesNotExist:
                return False
            patron.is_active = True
            patron.activation_key = None
            patron.save()
            return patron
        return False
    
    def create_inactive(self, username, email, password, send_email=True):
        """
        Create a new, inactive ``Patron`` and email its activation key to the
        ``Patron``, returning the new ``Patron``.
        
        To disable the email, call with ``send_email=False``.
        """
        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        activation_key = hashlib.sha1(salt + email).hexdigest()
        
        new_patron = self.create_user(username, email, password)
        new_patron.is_active = False
        new_patron.activation_key = activation_key
        new_patron.save()
        
        if send_email:
            new_patron.send_activation_email()
        return new_patron
        
    
    def delete_expired(self):
        """
        Remove expired instances of ``Patron``s.
        """
        for patron in self.filter(is_active=False):
            if patron.is_expired():
                patron.delete()
    
    def last_joined(self):
        return self.filter(
            ~Q(avatar=None)
        ).order_by('-date_joined')
    
    def last_joined_near(self, l):
        return self.filter(
            ~Q(avatar=None),
            ~Q(default_address=None),
        ).distance(
            l, field_name='default_address__position'
        ).extra(
            select={'joined': 'date(date_joined)'}
        ).order_by('-joined', 'distance')
    