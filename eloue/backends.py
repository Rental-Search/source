# coding=utf-8
from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from provider.forms import OAuthValidationError
from rest_framework import exceptions
from rest_framework.authentication import OAuth2Authentication
from rest_framework.compat import oauth2_provider, provider_now


class EloueAuthBackend(ModelBackend):

    def authenticate(self, username=None, password=None, **kwargs):
        user = super(EloueAuthBackend, self).authenticate(username, password, **kwargs)
        if user and not user.is_active:
            if user.login_count < settings.NON_ACTIVE_LOGIN_COUNT:
                user.login_count += 1
                user.save()
            else:
                raise OAuthValidationError({'error': 'user_inactive'})
        return user


class EloueRestAuthBackend(OAuth2Authentication):

    def authenticate_credentials(self, request, access_token):
        """
        Authenticate the request, given the access token.
        """

        try:
            token = oauth2_provider.oauth2.models.AccessToken.objects.select_related('user')
            # provider_now switches to timezone aware datetime when
            # the oauth2_provider version supports to it.
            token = token.get(token=access_token, expires__gt=provider_now())
        except oauth2_provider.oauth2.models.AccessToken.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token')

        user = token.user

        if not user.is_active and user.login_count > settings.NON_ACTIVE_LOGIN_COUNT:
            msg = 'User inactive or deleted: %s' % user.username
            raise exceptions.AuthenticationFailed(msg)

        return user, token
