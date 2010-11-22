# -*- coding: utf-8 -*-
from decimal import Decimal as D

import django.forms as forms
from django.conf import settings
from django.core.validators import EMPTY_VALUES
from django.utils.translation import ugettext as _

from haystack.forms import SearchForm
from mptt.forms import TreeNodeChoiceField

from eloue.geocoder import GoogleGeocoder
from eloue.products.fields import FacetField
from eloue.products.models import PatronReview, ProductReview, Product, Category
from eloue.products.utils import Enum


SORT = Enum([
    ('geo_distance', 'NEAR', _(u"Les plus proches")),
    ('created_at', 'RECENT', _(u"Les plus récentes")),
    ('price', 'LOW_PRICE', _(u"Les pris les plus bas")),
    ('-price', 'HIGH_PRICE', _(u"Les pris les plus haut")),
])

DEFAULT_RADIUS = getattr(settings, 'DEFAULT_RADIUS', 50)


class FacetedSearchForm(SearchForm):
    q = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={'class': 'inb'}))
    l = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={'class': 'inb'}))
    r = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'class': 'ins'}))
    sort = forms.ChoiceField(required=False, choices=SORT, widget=forms.HiddenInput())
    price = FacetField(label=_(u"Prix"), pretty_name=_("par-prix"), required=False)
    categories = FacetField(label=_(u"Catégorie"), pretty_name=_("par-categorie"), required=False, widget=forms.HiddenInput())
    
    def clean_r(self):
        radius = self.cleaned_data.get('r', None)
        if radius in EMPTY_VALUES:
            radius = DEFAULT_RADIUS
        return radius
    
    def search(self):
        if self.is_valid():
            sqs = self.searchqueryset
            suggestions = None
            
            query = self.cleaned_data.get('q', None)
            if query:
                sqs = self.searchqueryset.auto_query(query).highlight()
                suggestions = sqs.spelling_suggestion()
            
            location, radius = self.cleaned_data.get('l', None), self.cleaned_data.get('r', DEFAULT_RADIUS)
            if location:
                name, (lat, lon) = GoogleGeocoder().geocode(location)
                sqs = sqs.spatial(lat=lat, long=lon, radius=radius, unit='km')
            
            if self.load_all:
                sqs = sqs.load_all()
                        
            for key in self.cleaned_data.keys():
                if self.cleaned_data[key] and key not in ["q", "l", "r", "sort"]:
                    sqs = sqs.narrow("%s:%s" % (key, self.cleaned_data[key]))
        
            if self.cleaned_data['sort']:
                sqs = sqs.order_by(self.cleaned_data['sort'])
        
            return sqs, suggestions
        else:
            return self.searchqueryset, None
    

class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = PatronReview
        exclude = ('created_at', 'ip', 'reviewer', 'patron')
    

class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        exclude = ('created_at', 'ip', 'reviewer', 'product')
    

class ProductForm(forms.ModelForm):
    category = TreeNodeChoiceField(queryset=Category.tree.all(), empty_label="Choisissez une catégorie", level_indicator=u'--', widget=forms.Select(attrs={'class': 'selm'}))
    summary = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'inm'}))
    picture_id = forms.IntegerField(required=False, widget=forms.HiddenInput())
    picture = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'inm'}))
    price = forms.DecimalField(required=True, widget=forms.TextInput(attrs={'class': 'inm price'}))
    deposit_amount = forms.DecimalField(initial=0, required=False, max_digits=8, decimal_places=2, widget=forms.TextInput(attrs={'class': 'inm price'}))
    quantity = forms.IntegerField(initial=1, widget=forms.TextInput(attrs={'class': 'inm price'}))
    description = forms.Textarea()
    
    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity < 1:
            raise forms.ValidationError(_(u"Vous devriez au moins louer un object"))
        return quantity
    
    def clean_deposit_amount(self):
        deposit_amount = self.cleaned_data['deposit_amount']
        if deposit_amount in EMPTY_VALUES:
            deposit_amount = D('0')
        return deposit_amount
    
    def clean_picture(self):
        picture = self.cleaned_data['picture']
        picture_id = self.cleaned_data['picture_id']
        if not (picture or picture_id):
            raise forms.ValidationError(_(u"Vous devriez ajouter une photo."))
    
    class Meta:
        model = Product
        fields = ('category', 'summary', 'picture_id', 'picture', 'price', 'deposit_amount', 'quantity', 'description')
    
