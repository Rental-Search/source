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


class ProductSearchForm(forms.Form):
    q = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'inb'}))
    where = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'inb'}))


class FacetedSearchForm(SearchForm):
    q = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={'class':'inb'}))
    where = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={'class':'inb'}))
    radius = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'class':'ins'}))
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
    category = TreeNodeChoiceField(queryset=Category.tree.all(), empty_label="---------", level_indicator=u'--', widget=forms.Select(attrs={'style':'100%'}))
    summary = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'inb'}))
    picture_id = forms.IntegerField(required=False, widget=forms.HiddenInput())
    picture = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class':'inb pic'}))
    price = forms.DecimalField(required=True, widget=forms.TextInput(attrs={'class':'inb price'}))
    deposit_amount = forms.DecimalField(required=True, widget=forms.TextInput(attrs={'class':'inb price'}))
    quantity = forms.IntegerField(initial=1, widget=forms.TextInput(attrs={'class':'inb qty'}))
    description = forms.Textarea()
    
    def clean_picture(self):
        picture = self.cleaned_data['picture']
        picture_id = self.cleaned_data['picture_id']
        if not (picture or picture_id):
            raise forms.ValidationError(_(u"Vous devriez ajouter une photo."))
    
    class Meta:
        model = Product
        fields = ('category', 'summary', 'picture_id', 'picture', 'price', 'deposit_amount', 'quantity', 'description')
    
