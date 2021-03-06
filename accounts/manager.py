# -*- coding: utf-8 -*-
import hashlib
import random
import re

from django.contrib.auth.models import UserManager
from django.contrib.gis.db.models import GeoManager
from django.db.models import Q
from django.utils import timezone
from django.template.defaultfilters import slugify

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
        
        new_patron = self.create_user(
            username, email, password,
            is_active=False, activation_key=activation_key
        )
        
        if send_email:
            new_patron.send_activation_email()
        return new_patron

    def _create_user(self, username, email, password,
                     is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        if not email:
            raise ValueError('The given email must be set')
        now = timezone.now()
        email = self.normalize_email(email)
        slug = extra_fields.pop('slug', None) or slugify(username)
        user = self.model(username=username, email=email,
                          is_staff=is_staff, last_login=now,
                          is_superuser=is_superuser, slug=slug,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.full_clean()
        user.save(using=self._db)
        return user
    
    def delete_expired(self):
        """
        Remove expired instances of ``Patron``s.
        """
        for patron in self.filter(is_active=False):
            if patron.is_expired():
                patron.delete()
    
    def last_joined(self):
        return self.filter(
            #~Q(avatar=None)
        ).order_by('-date_joined')
    
    def last_joined_near(self, l):
        return self.filter(
            #~Q(avatar=None),
            ~Q(default_address=None),
        ).distance(
            l, field_name='default_address__position'
        ).extra(
            select={'joined': 'date(date_joined)'}
        ).order_by('-joined', 'distance')
    