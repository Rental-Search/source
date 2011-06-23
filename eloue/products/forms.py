# -*- coding: utf-8 -*-
import re
from decimal import Decimal as D

import django.forms as forms
from django.conf import settings
from django.core.validators import EMPTY_VALUES
from django.utils.translation import ugettext as _

from haystack.forms import SearchForm
from mptt.forms import TreeNodeChoiceField

from eloue.geocoder import GoogleGeocoder
from eloue.products.fields import FacetField
from eloue.products.models import Alert, PatronReview, ProductReview, Product, Picture, Category, UNIT, PAYMENT_TYPE
from eloue.products.utils import Enum


SORT = Enum([
    ('geo_distance', 'NEAR', _(u"Les plus proches")),
    ('-created_at', 'RECENT', _(u"Les plus récentes")),
    ('price', 'LOW_PRICE', _(u"Les pris les plus bas")),
    ('-price', 'HIGH_PRICE', _(u"Les pris les plus haut")),
])

DEFAULT_RADIUS = getattr(settings, 'DEFAULT_RADIUS', 50)


class FacetedSearchForm(SearchForm):
    q = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={'class': 'x9 inb', 'tabindex': '1'}))
    l = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={'class': 'x9 inb', 'tabindex': '2'}))
    r = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'class': 'ins'}))
    sort = forms.ChoiceField(required=False, choices=SORT, widget=forms.HiddenInput())
    price = FacetField(label=_(u"Prix"), pretty_name=_("par-prix"), required=False)
    categories = FacetField(label=_(u"Catégorie"), pretty_name=_("par-categorie"), required=False, widget=forms.HiddenInput())
    
    def clean_r(self):
        location = self.cleaned_data.get('l', None)
        radius = self.cleaned_data.get('r', None)
        if location not in EMPTY_VALUES and radius in EMPTY_VALUES:
            name, coordinates, radius = GoogleGeocoder().geocode(location)
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
                if suggestions:
                    suggestions = re.sub('AND\s*', '', suggestions)
                    suggestions = re.sub('[\(\)]+', '', suggestions)
                    suggestions = re.sub('django_ct:[a-zA-Z\.]*', '', suggestions)
                    suggestions = suggestions.strip()
                if suggestions == query:
                    suggestions = None
            
            location, radius = self.cleaned_data.get('l', None), self.cleaned_data.get('r', DEFAULT_RADIUS)
            if location:
                name, (lat, lon), _ = GoogleGeocoder().geocode(location)
                sqs = sqs.spatial(lat=lat, long=lon, radius=radius, unit='km')
            
            if self.load_all:
                sqs = sqs.load_all()
            
            for key in self.cleaned_data.keys():
                if self.cleaned_data[key] and key not in ["q", "l", "r", "sort"]:
                    sqs = sqs.narrow("%s_exact:%s" % (key, self.cleaned_data[key]))
            
            if self.cleaned_data['sort']:
                sqs = sqs.order_by(self.cleaned_data['sort'])
            return sqs, suggestions
        else:
            return self.searchqueryset, None
    

class AlertSearchForm(SearchForm):
    q = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={'class': 'inb'}))
    l = forms.CharField(label=_(u"Où ?"), required=False, max_length=100, widget=forms.TextInput(attrs={'class': 'inb', 'tabindex': '1'}))
    r = forms.IntegerField(label=_(u"Restreindre les résultats à un rayon de :"), required=False, widget=forms.TextInput(attrs={'class': 'ins', 'tabindex': '2'}))
    
    def clean_r(self):
        location = self.cleaned_data.get('l', None)
        radius = self.cleaned_data.get('r', None)
        if location not in EMPTY_VALUES and radius in EMPTY_VALUES:
            name, coordinates, radius = GoogleGeocoder().geocode(location)
        if radius in EMPTY_VALUES:
            radius = DEFAULT_RADIUS
        return radius
    
    def search(self):
        if self.is_valid():
            sqs = self.searchqueryset
            
            location, radius = self.cleaned_data.get('l', None), self.cleaned_data.get('r', DEFAULT_RADIUS)
            if location:
                name, (lat, lon), _ = GoogleGeocoder().geocode(location)
                sqs = sqs.spatial(lat=lat, long=lon, radius=radius, unit='km')
            
            if self.load_all:
                sqs = sqs.load_all()
            
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
    category = TreeNodeChoiceField(queryset=Category.tree.all(), empty_label=_(u"Choisissez une catégorie"), level_indicator=u'--', widget=forms.Select(attrs={'class': 'selm'}))
    summary = forms.CharField(label=_(u"Titre"), max_length=100, widget=forms.TextInput(attrs={'class': 'inm'}))
    picture_id = forms.IntegerField(required=False, widget=forms.HiddenInput())
    picture = forms.ImageField(label=_(u"Photo"), required=False, widget=forms.FileInput(attrs={'class': 'inm'}))
    deposit_amount = forms.DecimalField(label=_(u"Caution"), initial=0, required=False, max_digits=8, decimal_places=2, widget=forms.TextInput(attrs={'class': 'inm price'}), localize=True)
    quantity = forms.IntegerField(label=_(u"Quantité"), initial=1, widget=forms.TextInput(attrs={'class': 'inm price'}))
    description = forms.CharField(label=_(u"Description"), widget=forms.Textarea())
    payment_type = forms.ChoiceField(choices=PAYMENT_TYPE, required=False, widget=forms.Select(attrs={'class': 'selm'}))
    
    hour_price = forms.DecimalField(label=_(u"l'heure"), required=False, widget=forms.TextInput(attrs={'class': 'ins'}), localize=True)
    day_price = forms.DecimalField(label=_(u"la journée"), required=True, widget=forms.TextInput(attrs={'class': 'ins'}), localize=True)
    week_end_price = forms.DecimalField(label=_(u"le week-end"), required=False, widget=forms.TextInput(attrs={'class': 'ins'}), localize=True)
    week_price = forms.DecimalField(label=_(u"la semaine"), required=False, widget=forms.TextInput(attrs={'class': 'ins'}), localize=True)
    two_weeks_price = forms.DecimalField(label=_(u"les 15 jours"), required=False, widget=forms.TextInput(attrs={'class': 'ins'}), localize=True)
    month_price = forms.DecimalField(label=_(u"le mois"), required=False, widget=forms.TextInput(attrs={'class': 'ins'}), localize=True)
    
    
    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity < 1:
            raise forms.ValidationError(_(u"Vous devriez au moins louer un object"))
        return quantity
    
    def clean_deposit_amount(self):
        deposit_amount = self.cleaned_data.get('deposit_amount', None)
        if deposit_amount in EMPTY_VALUES:
            deposit_amount = D('0')
        return deposit_amount
    
    def clean_picture(self):
        picture = self.cleaned_data['picture']
        picture_id = self.cleaned_data['picture_id']
        if not (picture or picture_id):
            raise forms.ValidationError(_(u"Vous devriez ajouter une photo."))
    
    def clean_payment_type(self):
        payment_type = self.cleaned_data.get('payment_type', None)
        if payment_type in EMPTY_VALUES:
            payment_type = 1
        return payment_type
    
    class Meta:
        model = Product
        fields = ('category', 'summary', 'picture_id', 'picture', 'deposit_amount', 'quantity', 'description', 'payment_type')


class ProductEditForm(forms.ModelForm):
    category = TreeNodeChoiceField(queryset=Category.tree.all(), empty_label="Choisissez une catégorie", level_indicator=u'--')
    summary = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'inm'}))
    deposit_amount = forms.DecimalField(initial=0, required=False, max_digits=8, decimal_places=2, widget=forms.TextInput(attrs={'class': 'inm price'}), localize=True)
    quantity = forms.IntegerField(initial=1, widget=forms.TextInput(attrs={'class': 'inm price'}))
    picture = forms.ImageField(label=_(u"Photo"), required=False, widget=forms.FileInput(attrs={'class': 'inm'}))
    description = forms.CharField(label=_(u"Description"), widget=forms.Textarea())
    
    hour_price = forms.DecimalField(label=_(u"l'heure"), required=False, widget=forms.TextInput(attrs={'class': 'ins'}), localize=True)
    day_price = forms.DecimalField(label=_(u"la journée"), required=True, widget=forms.TextInput(attrs={'class': 'ins'}), localize=True)
    week_end_price = forms.DecimalField(label=_(u"le week-end"), required=False, widget=forms.TextInput(attrs={'class': 'ins'}), localize=True)
    week_price = forms.DecimalField(label=_(u"la semaine"), required=False, widget=forms.TextInput(attrs={'class': 'ins'}), localize=True)
    two_weeks_price = forms.DecimalField(label=_(u"les 15 jours"), required=False, widget=forms.TextInput(attrs={'class': 'ins'}), localize=True)
    month_price = forms.DecimalField(label=_(u"le mois"), required=False, widget=forms.TextInput(attrs={'class': 'ins'}), localize=True)
    
    def __init__(self, *args, **kwargs):
        super(ProductEditForm, self).__init__(*args, **kwargs)
        self.fields['category'].widget.attrs['class'] = "selm"
    
    def clean_deposit_amount(self):
        deposit_amount = self.cleaned_data.get('deposit_amount', None)
        if deposit_amount in EMPTY_VALUES:
            deposit_amount = D('0')
        return deposit_amount
    
    def clean_picture(self):
        picture = self.cleaned_data.get('picture', None)
        self.new_picture = picture
        return picture
    
    def save(self, *args, **kwargs):
        for unit in UNIT.keys():
            field = "%s_price" % unit.lower()
            if field in self.cleaned_data and self.cleaned_data[field]:
                instance, created = self.instance.prices.get_or_create(
                    unit=UNIT[unit],
                    defaults={'amount': self.cleaned_data[field]}
                )
                if not created:
                    instance.amount = self.cleaned_data[field]
                    instance.save()
        if self.new_picture:
            self.instance.pictures.all().delete()  # TODO : Do something less stupid here
            self.instance.pictures.add(Picture.objects.create(image=self.cleaned_data['picture']))
        return super(ProductEditForm, self).save(*args, **kwargs)
    
    class Meta:
        model = Product
        fields = ('category', 'summary', 'deposit_amount', 'quantity', 'description')
    

class ProductAdminForm(forms.ModelForm):
    category = TreeNodeChoiceField(queryset=Category.tree.all(), empty_label="Choisissez une catégorie", level_indicator=u'--')
    
    class Meta:
        model = Product


class AlertForm(forms.ModelForm):
    designation = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'inm'}))
    description = forms.CharField(label=_(u"Description"), widget=forms.Textarea())
    
    class Meta:
        model = Alert
        fields = ('description', 'designation')
    
