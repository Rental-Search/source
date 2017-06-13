# -*- coding: utf-8 -*-
import django.forms as forms


class BridgeForm(forms.Form):
	"""To send blob to slimpay and redirect the user on the slimpay plateform"""
	blob = forms.CharField(widget=forms.HiddenInput())