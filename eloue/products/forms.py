# -*- coding: utf-8 -*-
import re
from decimal import Decimal as D

import django.forms as forms
from form_utils.forms import BetterModelForm
from django.conf import settings
from django.core.validators import EMPTY_VALUES
from django.utils.translation import ugettext as _

from haystack.forms import SearchForm
from mptt.forms import TreeNodeChoiceField
from eloue.accounts.fields import DateSelectField
from eloue.accounts.models import Patron, COUNTRY_CHOICES, Address
from eloue.geocoder import GoogleGeocoder
from eloue.products.fields import FacetField, FRLicensePlateField
from eloue.products.models import Alert, PatronReview, ProductReview, Product, CarProduct, RealEstateProduct, Picture, Category, UNIT, PAYMENT_TYPE, ProductRelatedMessage, MessageThread
from eloue.products.widgets import PriceTextInput, CommentedSelectInput, CommentedTextInput
from eloue.products.utils import Enum
from django_messages.forms import ComposeForm
import datetime
from django.db.models import signals
from django_messages import utils
from django_messages.fields import CommaSeparatedUserField


from eloue.accounts.models import Address

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None
    
    
SORT = Enum([
    ('geo_distance', 'NEAR', _(u"Les plus proches")),
    ('-created_at', 'RECENT', _(u"Les plus récentes")),
    ('price', 'LOW_PRICE', _(u"Les pris les plus bas")),
    ('-price', 'HIGH_PRICE', _(u"Les pris les plus haut")),
])

DEFAULT_RADIUS = getattr(settings, 'DEFAULT_RADIUS', 50)


class FacetedSearchForm(SearchForm):
    q = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={'class': 'x9 inb search-box-q', 'tabindex': '1', 'placeholder': 'Que voulez-vous louer ?'}))
    l = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={'class': 'x9 inb', 'tabindex': '2', 'placeholder': 'Où voulez-vous louer?'}))
    r = forms.DecimalField(required=False, widget=forms.TextInput(attrs={'class': 'ins'}))
    sort = forms.ChoiceField(required=False, choices=SORT, widget=forms.HiddenInput())
    price = FacetField(label=_(u"Prix"), pretty_name=_("par-prix"), required=False)
    categories = FacetField(label=_(u"Catégorie"), pretty_name=_("par-categorie"), required=False, widget=forms.HiddenInput())
    renter = forms.CharField(required=False)

    def clean_r(self):
        location = self.cleaned_data.get('l', None)
        radius = self.cleaned_data.get('r', None)
        if location not in EMPTY_VALUES and radius in EMPTY_VALUES:
            name, coordinates, radius = GoogleGeocoder().geocode(location)
        if radius in EMPTY_VALUES:
            radius = DEFAULT_RADIUS
        return radius

    def clean_l(self):
        import re
        location = self.cleaned_data.get('l', None)
        if location:
            location = re.sub('^[0-9]* +(.*)', r'\1', location)
        return location

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
            
            status = self.cleaned_data.get('renter')
            if status == "particuliers":
                sqs = sqs.filter(pro=False)
            elif status == "professionnels":
                sqs = sqs.filter(pro=True)

            top_products = sqs.filter(is_top=True)[:3]
            if top_products:
                # XXX: ugly workaround because of SOLR-1658 (https://issues.apache.org/jira/browse/SOLR-1658)
                # as soon as we upgrad solr we should remove this workaround
                # I subclassed and modified the query string generator function in a SearchQuery class
                # to remove the outer parenthesis of a negation.
                from haystack.backends.solr_backend import SearchQuery
                from haystack.constants import DJANGO_CT, VALID_FILTERS, FILTER_SEPARATOR
                class BSQ(SearchQuery):
                    def build_query(self):
                        """
                        Interprets the collected query metadata and builds the final query to
                        be sent to the backend.
                        """
                        query = self.query_filter.as_query_string(self.build_query_fragment)

                        if not query:
                            # Match all.
                            query = self.matching_all_fragment()

                        if len(self.models):
                            models = sorted(['%s:%s.%s' % (DJANGO_CT, model._meta.app_label, model._meta.module_name) for model in self.models])
                            models_clause = ' OR '.join(models)

                            if query != self.matching_all_fragment():
                                if query.startswith('NOT'):
                                    final_query = '%s AND (%s)' % (query, models_clause)
                                else:
                                    final_query = '(%s) AND (%s)' % (query, models_clause)
                            else:
                                final_query = models_clause
                        else:
                            final_query = query

                        if self.boost:
                            boost_list = []

                            for boost_word, boost_value in self.boost.items():
                                boost_list.append(self.boost_fragment(boost_word, boost_value))

                            final_query = "%s %s" % (final_query, " ".join(boost_list))
                        
                        return final_query
                sqs.query = sqs.query._clone(BSQ)

                sqs = sqs.exclude(id__in=[product.id for product in top_products])

            for key in self.cleaned_data.keys():
                if self.cleaned_data[key] and key not in ["q", "l", "r", "sort", "renter"]:
                    sqs = sqs.narrow("%s_exact:%s" % (key, self.cleaned_data[key]))
            
            if self.cleaned_data['sort']:
                sqs = sqs.order_by(self.cleaned_data['sort'])
            else:
                sqs = sqs.order_by(SORT.RECENT)
            return sqs, suggestions, top_products
        else:
            return self.searchqueryset, None, top_products


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


class MessageEditForm(forms.Form):
    # used in the wizard, and in the reply
    subject = forms.CharField(label=_(u"Sujet"), widget=forms.TextInput(attrs={'class': 'inm'}), required=False)
    body = forms.CharField(label=_(u"Contenu"), widget=forms.Textarea(attrs={'class': 'inm'}))

    def __init__(self, *args, **kwargs):
        super(MessageEditForm, self).__init__(*args, **kwargs)
    
    def save(self, product, sender, recipient, parent_msg=None, offer=None):
        body = self.cleaned_data['body']
        subject = self.cleaned_data['subject']
        message_list = [] # WHY ... 
        if not hasattr(recipient, 'new_messages_alerted'):
            patron = Patron.objects.get(pk=recipient.pk)
            recipient = patron # Hacking to make messages work
        signals.post_save.connect(utils.new_message_email, ProductRelatedMessage)
        msg = ProductRelatedMessage(
          sender=sender,
          recipient=recipient,
          body=body,
          offer=offer
        )
        if parent_msg is not None:
            msg.parent_msg = parent_msg
            msg.thread = parent_msg.thread
            msg.subject = parent_msg.thread.subject
            if sender == msg.thread.sender:
                if msg.thread.recipient_archived:
                    msg.thread.recipient_archived = False
                    msg.thread.save()
            else:
                if msg.thread.sender_archived:
                    msg.thread.sender_archived = False
                    msg.thread.save()
            parent_msg.replied_at = datetime.datetime.now()
            parent_msg.save()
        else:
            thread = MessageThread(sender=sender, recipient=recipient, subject=subject)
            thread.last_message = msg
            thread.save()
            msg.thread = thread
            msg.subject = thread.subject
        msg.save()
        msg.thread.last_message = msg
        msg.thread.save()
        message_list.append(msg) # ... IS THIS ...
        if product:
            product.messages.add(msg.thread) # To implement a layer to wrap the message lib
        if notification:
            if parent_msg is not None:
                notification.send([recipient], "messages_reply_received", {'message': msg,})
            else:
                notification.send([recipient], "messages_received", {'message': msg,})
        return message_list # ... RETURNED?


def generate_choices(slugs, empty_value=_(u"Choisissez une catégorie")):
    if empty_value is not None:
        yield ('', empty_value)

    def _children(slugs):
        for slug in slugs:
            node = Category.on_site.get(slug=slug)
            for child in node.get_children():
                yield child
    for child in _children(slugs):
        descendants = child.get_descendants()
        if descendants:
            yield (
                _(child.name),
                [(descendant.pk, _(descendant.name)) for descendant in descendants]
            )
        else:
            yield (child.pk, _(child.name))


class ProductForm(BetterModelForm):
    summary = forms.CharField(label=_("Titre de l'annnonce"), max_length=100)
    picture_id = forms.IntegerField(required=True, widget=forms.HiddenInput())
    picture = forms.ImageField(label=_(u"Photo"), required=False)
    deposit_amount = forms.DecimalField(label=_(u"Dépôt de garantie"), initial=0, required=False, max_digits=8, decimal_places=2, widget=PriceTextInput(attrs={'class': 'price'}), localize=True, help_text=_(u"Nous conseillons de mettre la valeur actuelle de votre bien. Ce montant vous sera versé si votre objet est cassé ou irréparable."))
    quantity = forms.IntegerField(label=_(u"Quantité"), initial=1, widget=forms.TextInput(attrs={'class': 'price'}), help_text=_(u"Le locataire peut réserver plusieurs exemplaires si vous les possédez"))
    description = forms.CharField(label=_(u"Description"), widget=forms.Textarea(), help_text=_(u'Décrivez plus précisement votre objet, son état, comment et quand vous l\'utilisez.'))
    #payment_type = forms.ChoiceField(choices=PAYMENT_TYPE, required=False, widget=forms.Select(attrs={'class': 'selm'}))
    
    hour_price = forms.DecimalField(label=_(u"L'heure"), required=False, max_digits=10, decimal_places=2, min_value=D('0.01'), widget=PriceTextInput(attrs={'class': 'price'}), localize=True)
    day_price = forms.DecimalField(label=_(u"Tarif journée"), required=True, max_digits=10, decimal_places=2, min_value=D('0.01'), widget=PriceTextInput(attrs={'class': 'price'}), localize=True, help_text=_(u"20% de frais de commission (comprenant notamment l'assurance, le paiement en ligne,etc.) seront prélevés sur ce prix à chaque location."))
    week_end_price = forms.DecimalField(label=_(u"Le week-end"), required=False, max_digits=10, decimal_places=2, min_value=D('0.01'), widget=PriceTextInput(attrs={'class': 'price'}), localize=True)
    week_price = forms.DecimalField(label=_(u"La semaine"), required=False, max_digits=10, decimal_places=2, min_value=D('0.01'), widget=PriceTextInput(attrs={'class': 'price'}), localize=True)
    two_weeks_price = forms.DecimalField(label=_(u"Les 15 jours"), required=False, max_digits=10, decimal_places=2, min_value=D('0.01'), widget=PriceTextInput(attrs={'class': 'price'}), localize=True)
    month_price = forms.DecimalField(label=_(u"Le mois"), required=False, max_digits=10, decimal_places=2, min_value=D('0.01'), widget=PriceTextInput(attrs={'class': 'price'}), localize=True)

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.title = _(u'Ajouter un objet')
        self.header = _(u'Donnez envie aux e-loueurs potentiels de louer votre objets.')
        self.fields['category'] = forms.TypedChoiceField(
            label=_(u"Catégorie"), coerce=lambda pk: Category.tree.get(pk=pk), 
            choices=generate_choices((cat.slug for cat in Category.on_site.filter(parent=None) if cat.slug not in ['auto-et-moto', 'hebergement', 'motors', 'automobile', 'location-saisonniere']))
        )

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity < 1:
            raise forms.ValidationError(_(u"Vous devez au moins louer un object"))
        return quantity
    
    def clean_deposit_amount(self):
        deposit_amount = self.cleaned_data.get('deposit_amount', None)
        if deposit_amount in EMPTY_VALUES:
            deposit_amount = D('0')
        return deposit_amount

    def clean_picture(self):
        picture = self.cleaned_data.get('picture')
        picture_id = self.cleaned_data.get('picture_id')
        if not (picture or picture_id):
            raise forms.ValidationError(_(u"Vous devez ajouter une photo."))
        return picture

    def clean_payment_type(self):
        payment_type = self.cleaned_data.get('payment_type', None)
        if payment_type in EMPTY_VALUES:
            payment_type = 1
        return payment_type
    
    class Meta:
        model = Product
        fieldsets = [
            ('category', {'fields': ['category'], 'legend': _(u'Choisissez une catégorie')}),
            ('informations de l\'objet', {
                'fields': ['summary', 'picture_id', 'picture', 'description', 'quantity'], 
                'legend': _(u'Informations')}),
            ('price', {'fields': ['day_price', 'deposit_amount'], 
                        'legend': _(u'Prix de la location')}),
            ('price_detail', {
                'fields': ['hour_price', 'week_end_price', 'week_price', 'two_weeks_price', 'month_price'], 
                'legend': _(u'Grille des tarifs'),
                'description': 'La grille tarifaire permet d\'appliquer un tarif dégressif en fonction de la période. Ces prix ne sont pas obligatoires pour publier l\'annonce, il est possible de les ajouter plus tard.',
                'classes': ['prices-grid', 'hidden-fieldset']})
        ]


class CarProductForm(ProductForm):
    quantity = forms.IntegerField(widget=forms.HiddenInput(), initial=1)
    summary = forms.CharField(required=False, widget=forms.HiddenInput(), max_length=255)
    description = forms.CharField(label=_(u"Description"), widget=forms.Textarea(), help_text=_(u'Décrivez plus précissément votre véhicule, son état, ses particularités.'))
    deposit_amount = forms.DecimalField(label=_(u"Dépôt de garantie"), required=False, max_digits=8, decimal_places=2, widget=PriceTextInput(attrs={'class': 'price'}), localize=True, help_text=_(u"Nous conseillons un dépôt de garantie de 2000€, qui correspond au montant de la franchise de l'assurance voiture. en cas de vol."))
    licence_plate = FRLicensePlateField(label=_(u'N° d\'immatriculation'), required=True)
    first_registration_date = DateSelectField(label=_(u'1er mise en circulation'))


    def __init__(self, *args, **kwargs):
        super(CarProductForm, self).__init__(*args, **kwargs)
        self.title = _(u'Ajouter une voiture')
        self.header = _(u'Votre voiture peut être très utile. Donnez envie aux e-loueurs potentiels de louer votre véhicule.')
        self.fields['category'] = forms.TypedChoiceField(
            label=_(u"Catégorie"), coerce=lambda pk: Category.tree.get(pk=pk), 
            choices=generate_choices(('automobile',))
        )

    def clean(self):
        self.cleaned_data['summary'] = u'{brand} - {model}'.format(
            brand=self.cleaned_data.get('brand',''), model=self.cleaned_data.get('model', ''))
        return self.cleaned_data

    class Meta:
        model = CarProduct
        fieldsets = [
            ('category', {'fields': ['category'], 'legend': _(u'Type de véhicule')}),
            ('informations', {
                'fields': ['brand', 'summary', 'model', 'picture_id', 'picture', 'description'], 
                'legend': _(u'Description du véhicule')
                }),
            ('car_characteristics', {
                'fields': ['seat_number', 'door_number', 'fuel', 'transmission', 'mileage', 'consumption'],
                'legend': _(u'Caractéristique du véhicule'),
                }),
            ('assurancies_informations', {
                'fields': ['tax_horsepower', 'licence_plate', 'first_registration_date'],
                'legend': _(u'Informations pour l\'assurance'),
                'description': _(u'Ces informations servent à assurer le véhicule pendant la location <a href=\"#\">(En savoir plus)</a>.'),
                }),
            ('options', {
                'fields': ['air_conditioning', 'power_steering', 
                    'cruise_control', 'gps', 'baby_seat', 'roof_box', 
                    'bike_rack', 'snow_tires', 'snow_chains', 
                    'ski_rack', 'cd_player', 'audio_input'],
                'legend': _(u'Options & accessoires'),
                }),
            ('price', {
                'fields': ['day_price', 'deposit_amount', 'km_included', 'costs_per_km'], 
                'legend': _(u'Prix de la location')
                }),
            ('price_detail', {
                'fields': ['hour_price', 'week_end_price', 'week_price', 'two_weeks_price', 'month_price'], 
                'legend': _(u'Grille des tarifs'),
                'description': _(u'La grille tarifaire permet d\'appliquer un tarif dégressif en fonction de la période. Ces prix ne sont pas obligatoires pour publier l\'annonce, il est possible de les ajouter plus tard.'),
                'classes': ['prices-grid', 'hidden-fieldset']
                })
            ]
        widgets = {
            'seat_number': CommentedSelectInput(info_text=_(u'place(s)')),
            'door_number': CommentedSelectInput(info_text=_(u'porte(s)')),
            'consumption': CommentedSelectInput(info_text=_(u'litre/100km')),
            'tax_horsepower': CommentedSelectInput(info_text=_(u'CV')),
            'km_included': CommentedTextInput(info_text=_(u'Km')),
            'costs_per_km': CommentedTextInput(info_text=_(u'€/Km'))
        }


class RealEstateForm(ProductForm):
    quantity = forms.IntegerField(widget=forms.HiddenInput(), initial=1)
    description = forms.CharField(label=_(u"Description"), widget=forms.Textarea(), help_text=_(u'Décrivez les spécifités de votre logement et insistez sur ce qui le rend exceptionnel.'))
    deposit_amount = forms.DecimalField(label=_(u"Dépôt de garantie"), required=False, max_digits=8, decimal_places=2, widget=PriceTextInput(attrs={'class': 'price'}), localize=True, help_text=_(u"Nous conseillons un dépôt de garantie de 75€. Ceci correspond au montant de la franchise de l'assurance."))
    day_price = forms.DecimalField(label=_(u"Prix par nuit"), required=True, max_digits=10, decimal_places=2, min_value=D('0.01'), widget=PriceTextInput(attrs={'class': 'price'}), localize=True, help_text=_(u"Prix de location à la journée"))

    def __init__(self, *args, **kwargs):
        super(RealEstateForm, self).__init__(*args, **kwargs)
        self.title = _(u'Ajouter un logement')
        self.header = _(u'Votre logement est unique. Donnez envie aux e-loueurs potentiels de venir y séjourner.')
        self.fields['category'] = forms.TypedChoiceField(
            label=_(u"Catégorie"), coerce=lambda pk: Category.tree.get(pk=pk), 
            choices=generate_choices(('location-saisonniere', ))
        )

    class Meta:
        model = RealEstateProduct
        fieldsets = [
            ('category', {'fields': ['category'], 'legend': _(u'Choisissez une catégorie')}),
            ('informations du logement', {
                'fields': ['summary', 'picture_id', 'picture', 'description'], 
                'legend': _(u'Informations')}),
            ('real_estate_description', {
                'fields' : ['capacity', 'private_life', 'chamber_number', 'rules'],
                'legend' : _(u'Description du lieu')}),
            ('service_included', {
                'fields': [
                    'air_conditioning', 'breakfast', 'balcony', 'lockable_chamber', 
                    'towel', 'lift', 'family_friendly', 'gym', 'accessible', 
                    'heating', 'jacuzzi', 'chimney', 'internet_access', 
                    'kitchen', 'parking', 'smoking_accepted', 'ideal_for_events',
                    'tv', 'washing_machine', 'tumble_dryer', 'computer_with_internet'
                ],
                'legend': _(u'Service inclus')}),
            ('price', {
                'fields': ['day_price', 'deposit_amount'], 
                'legend': _(u'Prix de la location')}),
            ('price_detail', {
                'fields': ['hour_price', 'week_end_price', 'week_price', 'two_weeks_price', 'month_price'], 
                'legend': _(u'Grille des tarifs'),
                'description': 'La grille tarifaire permet d\'appliquer un tarif dégressif en fonction de la période. Ces prix ne sont pas obligatoires pour publier l\'annonce, il est possible de les ajouter plus tard.',
                'classes': ['prices-grid', 'hidden-fieldset']})]
        widgets = {
            'capacity': CommentedSelectInput(info_text=_(u'persone(s)')),
            'chamber_number': CommentedSelectInput(info_text=_(u'chambre(s)'))
        }


class ProductEditForm(BetterModelForm):
    picture = forms.ImageField(label=_(u"Photo"), required=False, widget=forms.FileInput(attrs={'class': 'inm'}))
    deposit_amount = forms.DecimalField(label=_(u"Dépôt de garantie"), initial=0, required=False, max_digits=8, decimal_places=2, widget=PriceTextInput(attrs={'class': 'price'}), localize=True, help_text=_(u"Montant utilisé en cas de dédomagement"))
    quantity = forms.IntegerField(label=_(u"Quantité"), initial=1, widget=forms.TextInput(attrs={'class': 'price'}), help_text=_(u"Le locataire peut réserver plusieurs exemplaires si vous les possédez"))


    def __init__(self, *args, **kwargs):
        super(ProductEditForm, self).__init__(*args, **kwargs)
        self.fields['category'] = forms.TypedChoiceField(
            label=_(u"Catégorie"), coerce=lambda pk: Category.tree.get(pk=pk), 
            choices=generate_choices(
                (cat.slug for cat in Category.on_site.filter(parent=None) if cat.slug not in ['auto-et-moto', 'hebergement', 'motors', 'automobile', 'location-saisonniere']), None
            )
        )
    class Meta:
        model = Product
        fieldsets = [
            ('category', {'fields': ['category'], 'legend': _(u'Catégorie')}),
            ('informations', {
                'fields': ['summary', 'picture', 'description', 'quantity', 'deposit_amount'], 
                'legend': _(u'Informations')}),
        ]

    def save(self, *args, **kwargs):
        if self.new_picture:
            self.instance.pictures.all().delete() 
            self.instance.pictures.add(Picture.objects.create(image=self.cleaned_data['picture']))
        return super(ProductEditForm, self).save(*args, **kwargs)
    
    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity < 1:
            raise forms.ValidationError(_(u"Vous devez au moins louer un object"))
        return quantity
    
    def clean_deposit_amount(self):
        deposit_amount = self.cleaned_data.get('deposit_amount', None)
        if deposit_amount in EMPTY_VALUES:
            deposit_amount = D('0')
        return deposit_amount
    
    def clean_picture(self):
        picture = self.cleaned_data.get('picture', None)
        self.new_picture = picture
        return picture

    def clean_payment_type(self):
        payment_type = self.cleaned_data.get('payment_type', None)
        if payment_type in EMPTY_VALUES:
            payment_type = 1
        return payment_type

class CarProductEditForm(ProductEditForm):
    summary = forms.CharField(required=False, widget=forms.HiddenInput(), max_length=255)
    first_registration_date = DateSelectField()
    licence_plate = FRLicensePlateField(label=_(u'N° d\'immatriculation'), required=True)
    first_registration_date = DateSelectField(label=_(u'1er mise en circulation'))

    def __init__(self, *args, **kwargs):
        super(CarProductEditForm, self).__init__(*args, **kwargs)
        del self.fields['quantity']
        self.fields['category'] = forms.TypedChoiceField(
            label=_(u"Catégorie"), coerce=lambda pk: Category.tree.get(pk=pk), 
            choices=generate_choices(('automobile',), None)
        )

    def clean(self):
        if self.errors:
            return self.cleaned_data
        self.cleaned_data['summary'] = u'{brand} - {model}'.format(**self.cleaned_data)
        return self.cleaned_data

    class Meta:
        model = CarProduct
        fieldsets = [
            ('category', {'fields': ['category'], 'legend': _(u'Type de véhicule')}),
            ('informations', {
                'fields': ['summary', 'brand', 'model', 'picture', 'description', 'deposit_amount', 'km_included', 'costs_per_km'], 
                'legend': _(u'Description du véhicule')
                }),
            ('car_characteristics', {
                'fields': ['seat_number', 'door_number', 'fuel', 'transmission', 'mileage', 'consumption'],
                'legend': _(u'Caractéristique du véhicule'),
                }),
            ('assurancies_informations', {
                'fields': ['tax_horsepower', 'licence_plate', 'first_registration_date'],
                'legend': _(u'Informations pour l\'assurance'),
                'description': _(u'Ces informations servent à assurer le véhicule pendant la location <a href=\"#\">(En savoir plus)</a>.'),
                }),
            ('options', {
                'fields': ['air_conditioning', 'power_steering', 
                    'cruise_control', 'gps', 'baby_seat', 'roof_box', 
                    'bike_rack', 'snow_tires', 'snow_chains', 
                    'ski_rack', 'cd_player', 'audio_input'],
                'legend': _(u'Options & accessoires'),
                })
        ]           
        widgets = {
            'seat_number': CommentedSelectInput(info_text=_(u'place(s)')),
            'door_number': CommentedSelectInput(info_text=_(u'porte(s)')),
            'consumption': CommentedSelectInput(info_text=_(u'litre/100km')),
            'tax_horsepower': CommentedSelectInput(info_text=_(u'CV')),
            'km_included': CommentedTextInput(info_text=_(u'Km')),
            'costs_per_km': CommentedTextInput(info_text=_(u'€/Km'))
        }

class RealEstateEditForm(ProductEditForm):
    def __init__(self, *args, **kwargs):
        super(RealEstateEditForm, self).__init__(*args, **kwargs)
        self.fields['category'] = forms.TypedChoiceField(
            label=_(u"Catégorie"), coerce=lambda pk: Category.tree.get(pk=pk), 
            choices=generate_choices(('location-saisonniere', ), None)
        )
        del self.fields['quantity']
    
    class Meta:
        model = RealEstateProduct
        fieldsets = [
            ('category', {'fields': ['category'], 'legend': _(u'Choisissez un catégorie')}),
            ('informations', {
                'fields': ['summary', 'picture', 'description'], 
                'legend': _(u'Informations')}),
            ('real_estate_description', {
                'fields' : ['capacity', 'private_life', 'chamber_number', 'rules'],
                'legend' : _(u'Description du lieu')}),
            ('service_included', {
                'fields': [
                    'air_conditioning', 'breakfast', 'balcony', 'lockable_chamber', 
                    'towel', 'lift', 'family_friendly', 'gym', 'accessible', 
                    'heating', 'jacuzzi', 'chimney', 'internet_access', 'kitchen', 
                    'parking', 'smoking_accepted', 'ideal_for_events', 'tv', 
                    'washing_machine', 'tumble_dryer', 'computer_with_internet'
                ],
                'legend': _(u'Service inclus')})
        ]

     

class ProductAddressEditForm(BetterModelForm):
    addresses__address1 = forms.CharField(label=_(u"Rue"), max_length=255, required=False)
    addresses__zipcode = forms.CharField(label=_(u"Code postal"), required=False, max_length=9)
    addresses__city = forms.CharField(label=_(u"Ville"), required=False, max_length=255)
    addresses__country = forms.ChoiceField(label=(u"Pays"), choices=COUNTRY_CHOICES, initial=settings.LANGUAGE_CODE.split('-')[1].upper(), required=False)
    

    def __init__(self, *args, **kwargs):
        super(ProductAddressEditForm, self).__init__(*args, **kwargs)
        self.fields['address'].queryset = self.instance.owner.addresses.all()
        self.fields['address'].label = _(u"Adresse")
        self.fields['address'].required = False

    def clean(self):
        address = self.cleaned_data.get('address')
        address1 = self.cleaned_data['addresses__address1']
        zipcode = self.cleaned_data['addresses__zipcode']
        city = self.cleaned_data['addresses__city']
        country = self.cleaned_data['addresses__country']

        if not address and not (address1 and zipcode and city and country):
            self.cleaned_data['address'] = self.instance.address
            raise forms.ValidationError(_(u"Vous devez spécifiez une adresse"))
        if not any(self.errors) and not address:
            self.cleaned_data['address'] = Address(address1=address1, zipcode=zipcode, city=city, country=country, patron=self.instance.owner)
            self.cleaned_data['address'].save()
        return self.cleaned_data

    class Meta:
        model = Product
        fields = ('address', 'addresses__address1', 'addresses__zipcode', 'addresses__city', 'addresses__country')
        fieldsets = [
            ('address', {
                'fields': ['address'], 
                'legend': 'Adresse existante'}),
            ('new_address', {
                'fields': ['addresses__address1', 'addresses__zipcode', 'addresses__city', 'addresses__country'],
                'legend': 'Nouvelle adresse',
                'classes': ['new-address', 'hidden-fieldset']})
        ]

      
class ProductPriceEditForm(BetterModelForm):
    hour_price = forms.DecimalField(label=_(u"L'heure"), required=False, max_digits=10, decimal_places=2, min_value=D('0.01'), widget=PriceTextInput(attrs={'class': 'price'}), localize=True)
    day_price = forms.DecimalField(label=_(u"La journée"), required=True, max_digits=10, decimal_places=2, min_value=D('0.01'), widget=PriceTextInput(attrs={'class': 'price'}), localize=True)
    week_end_price = forms.DecimalField(label=_(u"Le week-end"), required=False, max_digits=10, decimal_places=2, min_value=D('0.01'), widget=PriceTextInput(attrs={'class': 'price'}), localize=True)
    week_price = forms.DecimalField(label=_(u"La semaine"), required=False, max_digits=10, decimal_places=2, min_value=D('0.01'), widget=PriceTextInput(attrs={'class': 'price'}), localize=True)
    two_weeks_price = forms.DecimalField(label=_(u"Les 15 jours"), required=False, max_digits=10, decimal_places=2, min_value=D('0.01'), widget=PriceTextInput(attrs={'class': 'price'}), localize=True)
    month_price = forms.DecimalField(label=_(u"Le mois"), required=False, max_digits=10, decimal_places=2, min_value=D('0.01'), widget=PriceTextInput(attrs={'class': 'price'}), localize=True)

    def save(self, *args, **kwargs):
        for unit in UNIT.keys():
            field = "%s_price" % unit.lower()
            if field in self.cleaned_data:
                if self.cleaned_data[field]:
                    instance, created = self.instance.prices.get_or_create(
                        unit=UNIT[unit],
                        defaults={'amount': self.cleaned_data[field]}
                    )
                    if not created:
                        instance.amount = self.cleaned_data[field]
                        instance.save()
                else:
                    #TODO: could have problems with seasonal prices
                    self.instance.prices.filter(unit=UNIT[unit]).delete()
    
    class Meta:
        model = Product
        fields = ('hour_price', 'day_price', 'week_end_price', 'week_price', 'two_weeks_price', 'month_price')
        fieldsets = [
            ('price', {
                'fields': ['day_price', 'deposit_amount'], 
                'legend': _(u'Prix de la location')}),
            ('price_detail', {
                'fields': ['hour_price', 'week_end_price', 'week_price', 'two_weeks_price', 'month_price'], 
                'legend': _(u'Grille des tarifs'),
                'description': 'La grille tarifaire permet d\'appliquer un tarif dégressif en fonction de la période. Ces prix ne sont pas obligatoires pour publier l\'annonce, il est possible de les ajouter plus tard.',
                'classes': ['prices-grid']})
        ]      


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


from eloue.products.models import ProductHighlight, ProductTopPosition

class HighlightForm(forms.ModelForm):
    class Meta:
        model = ProductHighlight

class TopPositionForm(forms.ModelForm):
    class Meta:
        model = ProductTopPosition
