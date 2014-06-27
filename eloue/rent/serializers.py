
from rest_framework.serializers import HyperlinkedModelSerializer

from rent import models

class BookingSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = models.Booking
        fields = ('uuid', 'started_at', 'ended_at', 'state', 'deposit_amount', 'insurance_amount', 'total_amount',
                  'currency', 'owner', 'borrower', 'product', 'contract_id', 'created_at', 'canceled_at')
        read_only_fields = fields

class CommentSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = models.Comment
        fields = ('id', 'booking', 'comment', 'note', 'created_at') # TODO: 'author'
        read_only_fields = ('id', 'created_at')

class SinisterSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = models.Sinister
        fields = ('uuid', 'sinister_id', 'description', 'patron', 'booking', 'product') # TBD: do we need sinister_id to be exposed? How it's going to be used?
        read_only_fields = ('uuid', 'sinister_id', 'patron', 'booking', 'product')
