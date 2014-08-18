
from rest_framework.serializers import HyperlinkedModelSerializer, ChoiceField, CharField #HyperlinkedRelatedField
from rest_framework.reverse import reverse

from rent import models
from rent.choices import COMMENT_TYPE_CHOICES

class BookingSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = models.Booking
        fields = ('uuid', 'started_at', 'ended_at', 'state', 'deposit_amount', 'insurance_amount', 'total_amount',
                  'currency', 'owner', 'borrower', 'product', 'contract_id', 'created_at', 'canceled_at')
        read_only_fields = fields

class CommentSerializer(HyperlinkedModelSerializer):
    #author = HyperlinkedRelatedField(source='type', view_name='patron-detail', read_only=True)
    author = CharField(source='type', read_only=True)
    rate = ChoiceField(source='note', choices=models.Comment._meta.get_field('note').choices)

    def transform_author(self, obj, value):
        obj_id = obj.booking.owner_id if value == COMMENT_TYPE_CHOICES.OWNER else obj.booking.borrower_id
        return reverse('patron-detail', args=(obj_id,),
            request=self.context['request'], format=self.context.get('format', None)
        )

    class Meta:
        model = models.Comment
        fields = ('id', 'author', 'booking', 'comment', 'rate', 'created_at', 'type')
        read_only_fields = ('id', 'created_at', 'type')

class SinisterSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = models.Sinister
        fields = ('uuid', 'sinister_id', 'description', 'patron', 'booking', 'product') # TBD: do we need sinister_id to be exposed? How it's going to be used?
        read_only_fields = ('uuid', 'sinister_id', 'patron', 'booking', 'product')
