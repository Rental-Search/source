# -*- coding: utf-8 -*-
import django.forms as forms
from django.utils.translation import ugettext as _

from haystack.forms import SearchForm
from mptt.forms import TreeNodeChoiceField

from eloue.products.fields import FacetField
from eloue.products.models import PatronReview, ProductReview, Product, Category
from eloue.products.utils import Enum

SORT = Enum([
    ('geo_distance', 'NEAR', _(u"Les plus proches")),
    ('created_at', 'RECENT', _(u"Les plus récentes")),
    ('price', 'LOW_PRICE', _(u"Les pris les plus bas")),
    ('-price', 'HIGH_PRICE', _(u"Les pris les plus haut")),
])

class FacetedSearchForm(SearchForm):
    q = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={'class':'big'}))
    where = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={'class':'big'}))
    radius = forms.IntegerField(required=False)
    sort = forms.ChoiceField(required=False, choices=SORT, widget=forms.HiddenInput())
    price = FacetField(label=_(u"Prix"), pretty_name=_("par-prix"), required=False)
    categories = FacetField(label=_(u"Catégorie"), pretty_name=_("par-categorie"), required=False, widget=forms.HiddenInput())
    
    def search(self):
        if self.is_valid():
            sqs = self.searchqueryset.auto_query(self.cleaned_data['q'])
            
            if self.load_all:
                sqs = sqs.load_all()
            
            for key in self.cleaned_data.keys():
                if self.cleaned_data[key] and key not in ["q", "where", "radius", "sort"]:
                    sqs = sqs.narrow("%s:%s" % (key, self.cleaned_data[key]))
        
            if self.cleaned_data['sort']:
                sqs = sqs.order_by(self.cleaned_data['sort'])
        
            return sqs
        else:
            return self.searchqueryset
    

class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = PatronReview
        exclude = ('created_at', 'ip', 'reviewer', 'patron')
    

class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        exclude = ('created_at', 'ip', 'reviewer', 'product')
    

class ProductForm(forms.ModelForm):
    category = TreeNodeChoiceField(queryset=Category.tree.all(), empty_label="---------", level_indicator=u'--')
    price = forms.DecimalField(required=True)
    picture = forms.ImageField()
    
    class Meta:
        model = Product
        exclude = ('is_allowed', 'owner', 'address', 'currency', 'is_archived')
    
