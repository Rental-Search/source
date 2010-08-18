# -*- coding: utf-8 -*-
import django.forms as forms

from eloue.accounts.models import Patron

class PatronChangeForm(forms.ModelForm):
    class Meta:
        model = Patron
    
