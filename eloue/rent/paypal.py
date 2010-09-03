# -*- coding: utf-8 -*-
from django.conf import settings

from paypalx import PaypalError, AdaptivePayments, AdaptiveAccounts

__all__ = ['PaypalError', 'accounts', 'payments']

accounts = AdaptiveAccounts(
    settings.PAYPAL_API_USERNAME,
    settings.PAYPAL_API_PASSWORD,
    settings.PAYPAL_API_SIGNATURE,
    settings.PAYPAL_API_APPLICATION_ID,
    settings.PAYPAL_API_EMAIL,
    sandbox = settings.USE_PAYPAL_SANDBOX
)

payments = AdaptivePayments(
    settings.PAYPAL_API_USERNAME, 
    settings.PAYPAL_API_PASSWORD, 
    settings.PAYPAL_API_SIGNATURE, 
    settings.PAYPAL_API_APPLICATION_ID, 
    settings.PAYPAL_API_EMAIL,
    sandbox = settings.USE_PAYPAL_SANDBOX
)
