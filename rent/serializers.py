# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from rest_framework.serializers import HyperlinkedRelatedField, RelatedField, get_component
from rest_framework import fields
from accounts.serializers import NestedUserSerializer
from products.serializers import NestedProductSerializer

from rent import models
from rent.choices import COMMENT_TYPE_CHOICES
from eloue.api import serializers

class SinisterSerializer(serializers.ModelSerializer):

    def full_clean(self, instance):
        instance = super(SinisterSerializer, self).full_clean(instance)
        if instance:
            if instance.booking:
                if instance.booking.product != instance.product:
                    self._errors.update({
                        'product': _(u'The booking is made on another product')
                    })
                    return None
                elif not (instance.patron == instance.booking.owner or instance.patron == instance.booking.borrower):
                    self._errors.update({
                        'booking': _(u'You are not owner or borrower of this booking')
                    })
                    return None

        return instance

    class Meta:
        model = models.Sinister
        fields = ('uuid', 'sinister_id', 'description', 'patron', 'booking', 'product') # TBD: do we need sinister_id to be exposed? How it's going to be used?
        read_only_fields = ('uuid', 'sinister_id')
        immutable_fields = ('patron', 'booking', 'product')

class NestedSinisterSerializer(serializers.NestedModelSerializerMixin, serializers.ModelSerializer):
    class Meta(SinisterSerializer.Meta):
        fields = ('uuid', 'description')

class BookingProductField(NestedProductSerializer):
    default_error_messages = {
        'own_product': _(u"Vous ne pouvez pas louer vos propres objets"),
    }

    def field_from_native(self, data, files, field_name, into):
        super(BookingProductField, self).field_from_native(data, files, field_name, into)
        value = into[field_name]
        self.validate(value)
        into['owner'] = value.owner

    def validate(self, value):
        super(BookingProductField, self).validate(value)
        if value.owner == self.context['request'].user:
            raise ValidationError(self.error_messages['own_product'])


class BookingSerializer(serializers.ModelSerializer):
    product = BookingProductField()
    owner = NestedUserSerializer(read_only=True)
    borrower = NestedUserSerializer()
    sinisters = NestedSinisterSerializer(read_only=True, required=False, many=True)

    def restore_object(self, attrs, instance=None):
        obj = super(BookingSerializer, self).restore_object(attrs, instance=instance)
        if instance is None:
            product = obj.product
            unit = product.calculate_price(obj.started_at, obj.ended_at)
            max_available = self.opts.model.calculate_available_quantity(product, obj.started_at, obj.ended_at)
            obj.quantity = quantity = min(obj.quantity or 1, max_available)
            obj.total_amount = unit[1] * quantity
            obj.ip = self.context['request'].META.get('REMOTE_ADDR', None)
        return obj

    class Meta:
        model = models.Booking
        fields = (
            'uuid', 'started_at', 'ended_at', 'state', 'deposit_amount', 'insurance_amount', 'total_amount',
            'currency', 'owner', 'borrower', 'product', 'contract_id', 'created_at', 'canceled_at', 'sinisters',
        )
        read_only_fields = (
            'state', 'deposit_amount', 'insurance_amount', 'total_amount',
            'currency', 'contract_id', 'created_at', 'canceled_at',
        )
        immutable_fields = ('started_at', 'ended_at', 'owner', 'borrower', 'product')
        range_fields = (('started_at', 'ended_at'),)

class BookingActionSerializer(serializers.ModelSerializer):
    action = fields.CharField(write_only=True, max_length=128)

    default_error_messages = {
        'invalid_action': _('Action %(action)s is not available for this state: %(state)s'),
    }

    def validate_action(self, attrs, source):
        action = attrs.pop(source)
        transitions = self.object.get_available_user_state_transitions(self.context['request'].user)
        for transition in transitions:
            if action == transition.method.__name__:
                # get_available_user_state_transitions return unbound method.
                # It must be bound manually.
                self.object._fsm_transition_method = transition.method.__get__(self.object)
                return attrs
        raise ValidationError(self.error_messages['invalid_action'] % dict(action=action, state=self.object.state))

    def save_object(self, obj, force_insert=False, force_update=False, using=None, update_fields=None, **kwargs):
        obj._fsm_transition_method(**kwargs)
        super(BookingActionSerializer, self).save_object(obj, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    class Meta:
        model = models.Booking
        fields = ('action',)

class CommentAuthorField(HyperlinkedRelatedField):
    default_error_messages = {
        'invalid_author': _('Author of the comment must be either owner or borrower of the related booking record'),
    }

    booking_field_names = {
        COMMENT_TYPE_CHOICES.OWNER: 'booking.owner',
        COMMENT_TYPE_CHOICES.BORROWER: 'booking.borrower',
    }

    def __init__(self, source='type', required=False, view_name='patron-detail', *args, **kwargs):
        super(CommentAuthorField, self).__init__(*args, source=source, required=required, view_name=view_name, **kwargs)

    def field_to_native(self, obj, field_name):
        """
        Given an object and a field name, returns the value that should be
        serialized for that field.

        Returns either 'owner' or 'borrower' from the related booking record.
        """
        if obj is not None:
            # override field name according to 'type'
            self.source = self.booking_field_names[obj.type]
        return super(CommentAuthorField, self).field_to_native(obj, field_name)

    def field_from_native(self, data, files, field_name, into):
        reverted_data = {}

        super(CommentAuthorField, self).field_from_native(data, files, field_name, reverted_data)
        author = reverted_data[self.source]

        user = self.parent.context['request'].user
        # force current user as the author if 'author' has not been provided,
        # or current user is not a team staff
        if not(user.is_staff and author is not None):
            author = user

        # safely auto-resolve 'booking' if not done yet
        if 'booking' in into:
            booking = into['booking']
        else:
            field = self.parent.fields['booking']
            field.initialize(parent=self.parent, field_name='booking')
            field.field_from_native(data, files, 'booking', reverted_data)
            booking = reverted_data['booking']

        author_id = author.pk
        if author_id == booking.owner_id:
            comment_type = COMMENT_TYPE_CHOICES.OWNER
        elif author_id == booking.borrower_id:
            comment_type = COMMENT_TYPE_CHOICES.BORROWER
        else:
            raise ValidationError(self.error_messages['invalid_author'])

        into[self.source] = comment_type

    def initialize(self, parent, field_name):
        """
        Called to set up a field prior to field_to_native or field_from_native.

        parent - The parent serializer.
        field_name - The name of the field being initialized.

        Prepares a queryset for the model field by using the default manager.
        Properly supports dot-separated field names (e.g. 'booking.owner')
        """
        field_name = 'booking.owner'
        # TODO: the code below should be provided upstream to fix the multi-component field names
        super(RelatedField, self).initialize(parent, field_name)
        if self.queryset is None and not self.read_only:
            model = self.parent.opts.model
            for component in field_name.split('.'):
                field = get_component(model, component)
                if hasattr(field, 'related'):  # Forward
                    model = field.related.model
                else:  # Reverse
                    model = field.field.rel.to
            self.queryset = model._default_manager.all()

class CommentSerializer(serializers.ModelSerializer):
    rate = fields.ChoiceField(source='note', choices=models.Comment._meta.get_field('note').choices)
    author = CommentAuthorField()

    class Meta:
        model = models.Comment
        fields = ('id', 'booking', 'comment', 'rate', 'created_at', 'author') # 'author' must follow after the 'booking'
        public_fields = ('id', 'booking', 'comment', 'rate', 'created_at', 'author')
        read_only_fields = ('created_at',)
        immutable_fields = ('booking', 'author')
