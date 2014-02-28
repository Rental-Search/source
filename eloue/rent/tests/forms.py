from django.test import TransactionTestCase
from django.db import transaction, IntegrityError

from eloue.rent.forms import BorrowerCommentForm, OwnerCommentForm
from eloue.rent.models import Booking, BorrowerComment, OwnerComment

class BorrowerCommentFormTest(TransactionTestCase):
    reset_sequences = True
    fixtures = ['category', 'patron', 'address', 'price', 'product', 'booking']

    def setUp(self):
        self.booking = Booking.objects.get(pk="1fac3d9f309c437b99f912bd08b09526")
    
    def test_form_ok(self):
        form = BorrowerCommentForm(
            {
                'note': u'5',
                'comment': u'bien',
            }
        )
        self.assertTrue(form.is_valid())
        self.assertRaises(IntegrityError, form.save)
        transaction.rollback()
        
        form = BorrowerCommentForm(
            {
                'note': u'5',
                'comment': u'bien',
            }, instance=BorrowerComment(booking=self.booking))
        self.assertTrue(form.is_valid())
        form.save()
        
    def test_form_error(self):
        form = BorrowerCommentForm(
            {
                'note': u'6',
                'comment': u'bien',
            }
        )
        self.assertFalse(form.is_valid())
        form = BorrowerCommentForm(
            {
                'note': u'6',
                'comment': u'',
            }
        )
        self.assertFalse(form.is_valid())