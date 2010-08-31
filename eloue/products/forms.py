# -*- coding: utf-8 -*-
import django.forms as forms
from django.utils.translation import ugettext as _

from haystack.forms import SearchForm

from eloue.products.fields import FacetField
from eloue.products.models import Review

class FacetedSearchForm(SearchForm):
    owner = FacetField(label=_(u"Loueur"), pretty_name=_("par-loueur"), required=False, widget=forms.HiddenInput)
    category = FacetField(label=_(u"Catégorie"), pretty_name=_("par-categorie"), required=False, widget=forms.HiddenInput)
    
    def search(self):
        sqs = super(FacetedSearchForm, self).search()
        
        for key in self.cleaned_data.keys():
            if self.cleaned_data[key] and key is not "q":
                sqs = sqs.narrow("%s:%s" % (key, self.cleaned_data[key]))
        
        return sqs
    

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        exclude = ('created_at', 'ip', 'reviewer')
    
