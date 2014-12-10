# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from operator import itemgetter

from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from django.utils.translation import ugettext as _
from django.db.models import get_model
from django.db import connection
from django.conf import settings

from rest_framework.test import APITestCase, APITransactionTestCase

from rent.choices import COMMENT_TYPE_CHOICES

def _location(name, *args, **kwargs):
    return reverse(name, args=args, kwargs=kwargs)


class AnonymousBookingTest(APITestCase):

    fixtures = ['patron', 'address', 'category', 'product', 'price', 'booking', 'comment', 'booking_creditcard']

    def test_booking_list_forbidden(self):
        response = self.client.get(_location('booking-list'))
        self.assertEquals(response.status_code, 401)

    def test_booking_show_forbidden(self):
        response = self.client.get(_location('booking-detail', pk='87ee8e9dec1d47c29ebb27e09bda8fc3'))
        self.assertEquals(response.status_code, 401)

    def test_booking_create_forbidden(self):
        response = self.client.post(_location('booking-list'))
        self.assertEquals(response.status_code, 401)

    def test_booking_pay_forbidden(self):
        response = self.client.put(_location('booking-pay', pk='87ee8e9dec1d47c29ebb27e09bda8fc3'))
        self.assertEquals(response.status_code, 401)

    def test_booking_accept_forbidden(self):
        response = self.client.put(_location('booking-accept', pk='87ee8e9dec1d47c29ebb27e09bda8fc3'))
        self.assertEquals(response.status_code, 401)

    def test_booking_reject_forbidden(self):
        response = self.client.put(_location('booking-reject', pk='87ee8e9dec1d47c29ebb27e09bda8fc3'))
        self.assertEquals(response.status_code, 401)

    def test_booking_cancel_forbidden(self):
        response = self.client.put(_location('booking-cancel', pk='87ee8e9dec1d47c29ebb27e09bda8fc3'))
        self.assertEquals(response.status_code, 401)


class BookingTest(APITransactionTestCase):
    reset_sequences = True
    fixtures = [
        'patron', 'booking_address', 'category', 'product', 'price', 'booking_api2', 'comment',
        'booking_creditcard', 'fake_payments'
    ]

    def setUp(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')
        connection.cursor().execute("select setval('rent_booking_contract_id_seq', %s);", [100])

    def test_booking_list(self):
        response = self.client.get(_location('booking-list'))
        self.assertEquals(response.status_code, 200, response.data)
        # check pagination data format in the response
        expected = {
            'count': 14,
            'previous': None,
        }
        self.assertDictContainsSubset(expected, response.data)
        self.assertIn('results', response.data)
        # check data
        self.assertEquals(min(response.data['count'], settings.REST_FRAMEWORK['PAGINATE_BY']), len(response.data['results']))

    def test_booking_get_by_id(self):
        response = self.client.get(_location('booking-detail', pk='87ee8e9dec1d47c29ebb27e09bda8fc3'))
        self.assertEquals(response.status_code, 200, response.data)

    def test_booking_create(self):
        response = self.client.post(_location('booking-list'), {
            'started_at': datetime.now() + timedelta(days=2),
            'ended_at': datetime.now() + timedelta(days=4),
            'product': _location('product-detail', pk=6),
        })
        self.assertEquals(response.status_code, 201, response.data)
        # check we got fields of the created instance in the response
        self.assertIn('uuid', response.data)
        # the currently authenticated user must be used on creation
        self.assertTrue(response.data['borrower']['id'], 1)
        # the owner must be taken from the product automatically
        self.assertTrue(response.data['owner']['id'], 4)

        # Location header must be properly set to redirect to the resource have just been created
        self.assertIn('Location', response)
        self.assertTrue(response['Location'].endswith(_location('booking-detail', pk=response.data['uuid'])))

    def test_booking_create_wrong_range(self):
        response = self.client.post(_location('booking-list'), {
            'started_at': datetime.now() + timedelta(days=4),
            'ended_at': datetime.now() + timedelta(days=2),
            'product': _location('product-detail', pk=6),
        })
        self.assertEquals(response.status_code, 400, response.data)
        self.assertIn('started_at', response.data['errors'], response.data)

    def test_booking_create_not_mine(self):
        response = self.client.post(_location('booking-list'), {
            'started_at': datetime.now() + timedelta(days=2),
            'ended_at': datetime.now() + timedelta(days=4),
            'product': _location('product-detail', pk=6),
            'borrower': _location('patron-detail', pk=2)
        })
        self.assertEquals(response.status_code, 201, response.data)
        # check we got fields of the created instance in the response
        self.assertIn('uuid', response.data)
        # the currently authenticated user must be used on creation
        self.assertEqual(response.data['borrower']['id'], 1)
        # the owner must be taken from the product automatically
        self.assertEqual(response.data['owner']['id'], 4)

        # Location header must be properly set to redirect to the resource have just been created
        self.assertIn('Location', response)
        self.assertTrue(response['Location'].endswith(_location('booking-detail', pk=response.data['uuid'])))

    def test_booking_create_borrower(self):
        response = self.client.post(_location('booking-list'), {
            'started_at': datetime.now() + timedelta(days=2),
            'ended_at': datetime.now() + timedelta(days=4),
            'product': _location('product-detail', pk=6),
            'borrower': _location('patron-detail', pk=4),
        })
        self.assertEquals(response.status_code, 201, response.data)
        # the currently authenticated user must be used on creation
        self.assertTrue(response.data['borrower']['id'], 1)

    def test_booking_create_own_product_error(self):
        response = self.client.post(_location('booking-list'), {
            'started_at': datetime.now() + timedelta(days=2),
            'ended_at': datetime.now() + timedelta(days=4),
            'product': _location('product-detail', pk=1),
        })
        self.assertEquals(response.status_code, 400, response.data)

    def test_booking_cancel_not_mine(self):
        response = self.client.put(_location('booking-cancel', '349ce9ba628abfdfc9cb3a72608dab68'))
        self.assertEqual(response.status_code, 404, response.data)

    def test_booking_pay_not_mine(self):
        response = self.client.put(_location('booking-pay', '349ce9ba628abfdfc9cb3a72608dab68'), {
            'expires': '0517',
            'holder_name': 'John Doe',
            'card_number': '4987654321098769',
            'cvv': '123',
        })
        self.assertEqual(response.status_code, 404, response.data)

    def test_booking_pay_new_card(self):
        response = self.client.put(_location('booking-pay', '87ee8e9dec1d47c29ebb27e09bdada43'), {
            'expires': '0517',
            'holder_name': 'John Doe',
            'card_number': '4987654321098769',
            'cvv': '123',
        })
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data['detail'], _(u'Transition performed'))

    def test_booking_pay_owner(self):
        self.client.login(username='lin.liu@e-loue.com', password='lin')

        response = self.client.put(_location('booking-pay', '87ee8e9dec1d47c29ebb27e09bdada43'), {
            'expires': '0517',
            'holder_name': 'John Doe',
            'card_number': '4987654321098769',
            'cvv': '123',
        })
        self.assertEqual(response.status_code, 403, response.data)

    def test_booking_accept(self):
        self.client.login(username='lin.liu@e-loue.com', password='lin')

        response = self.client.put(_location('booking-accept', '87ee8e9dec1d47c29ebb27e09bda89df'))
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data['detail'], _(u'Transition performed'))

    def test_booking_accept_borrower(self):
        response = self.client.put(_location('booking-accept', '87ee8e9dec1d47c29ebb27e09bda89df'))
        self.assertEqual(response.status_code, 403, response.data)

    def test_booking_contract(self):
        response = self.client.get(_location('booking-contract', '87ee8e9dec1d47c29ebb27e09bdacabd'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.startswith('%PDF'), "'{}'.startswith('%PDF')".format(response.content))

    def test_booking_incident(self):
        response = self.client.put(_location('booking-incident', '87ee8e9dec1d47c29ebb27e09bdafffa'), {
            'description': 'Description',
        })
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data['detail'], _(u'Transition performed'))

    def test_booking_accept_wrong_state(self):
        self.client.login(username='lin.liu@e-loue.com', password='lin')
        response = self.client.put(_location('booking-accept', '87ee8e9dec1d47c29ebb27e09bdada43'))
        self.assertEqual(response.status_code, 400, response.data)

    def test_booking_reject(self):
        self.client.login(username='lin.liu@e-loue.com', password='lin')

        response = self.client.put(_location('booking-reject', '87ee8e9dec1d47c29ebb27e09bda89df'))
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data['detail'], _(u'Transition performed'))

    def test_booking_reject_borrower(self):
        response = self.client.put(_location('booking-reject', '87ee8e9dec1d47c29ebb27e09bda89df'))
        self.assertEqual(response.status_code, 403, response.data)

    def test_booking_reject_wrong_state(self):
        self.client.login(username='lin.liu@e-loue.com', password='lin')

        response = self.client.put(_location('booking-reject', '87ee8e9dec1d47c29ebb27e09bdada43'))
        self.assertEqual(response.status_code, 400, response.data)

    def test_booking_cancel(self):
        self.client.login(username='lin.liu@e-loue.com', password='lin')

        response = self.client.put(_location('booking-cancel', '87ee8e9dec1d47c29ebb27e09bda89df'))
        self.assertEqual(response.status_code, 403, response.data)

    def test_booking_cancel_borrower(self):
        response = self.client.put(_location('booking-cancel', '87ee8e9dec1d47c29ebb27e09bda89df'))
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data['detail'], _(u'Transition performed'))

    @override_settings(TEST_MODE=True)
    def test_booking_pay_existing_card(self):
        response = self.client.put(_location('booking-pay', '87ee8e9dec1d47c29ebb27e09bdada43'), {
            'credit_card': _location('creditcard-detail', 3)
        })
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data['detail'], _(u'Transition performed'))

    def test_ordering(self):
        response = self.client.get(_location('booking-list'), {'ordering': 'state'})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEqual(
            response.data['results'],
            sorted(response.data['results'], key=itemgetter('state')))

    def test_reverse_ordering(self):
        response = self.client.get(_location('booking-list'), {'ordering': '-state'})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEqual(
            response.data['results'],
            sorted(response.data['results'], key=itemgetter('state'), reverse=True))

    def test_filter1(self):
        response = self.client.get(_location('booking-list'), {'total_amount': 20})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertGreater(response.data['count'], 0)
        self.assertEqual(response.data['results'], filter(lambda x: x['total_amount'] == 20, response.data['results']))
        self.assertEqual([], filter(lambda x: x['total_amount'] != 20, response.data['results']))

    def test_filter2(self):
        response = self.client.get(_location('booking-list'), {'total_amount': 10})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertGreater(response.data['count'], 0)
        self.assertEqual(response.data['results'], filter(lambda x: x['total_amount'] == 10, response.data['results']))
        self.assertEqual([], filter(lambda x: x['total_amount'] != 10, response.data['results']))


class StaffBookingTest(APITestCase):
    fixtures = ['patron_staff', 'booking_address', 'category', 'product', 'price', 'booking', 'comment', 'booking_creditcard']

    def setUp(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')

    def test_ordering(self):
        response = self.client.get(_location('booking-list'), {'ordering': 'state'})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEqual(
            response.data['results'],
            sorted(response.data['results'], key=itemgetter('state')))

    def test_reverse_ordering(self):
        response = self.client.get(_location('booking-list'), {'ordering': '-state'})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEqual(
            response.data['results'],
            sorted(response.data['results'], key=itemgetter('state'), reverse=True))

    def test_filter1(self):
        response = self.client.get(_location('booking-list'), {'total_amount': 20})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertGreater(response.data['count'], 0)
        self.assertEqual(response.data['results'], filter(lambda x: x['total_amount'] == 20, response.data['results']))
        self.assertEqual([], filter(lambda x: x['total_amount'] != 20, response.data['results']))

    def test_filter2(self):
        response = self.client.get(_location('booking-list'), {'total_amount': 10})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertGreater(response.data['count'], 0)
        self.assertEqual(response.data['results'], filter(lambda x: x['total_amount'] == 10, response.data['results']))
        self.assertEqual([], filter(lambda x: x['total_amount'] != 10, response.data['results']))


class AnonymousCommentTest(APITestCase):

    fixtures = ['patron', 'address', 'category', 'product', 'booking', 'comment']
    public_fields = ('id', 'author', 'booking', 'comment', 'rate')
    private_fields = tuple()

    def test_comment_list_forbidden(self):
        response = self.client.get(_location('picture-list'))
        self.assertEquals(response.status_code, 401)

    def test_comment_show_allowed(self):
        response = self.client.get(_location('comment-detail', pk=1))
        self.assertEquals(response.status_code, 200)

        for field in self.public_fields:
            self.assertIn(field, response.data, field)

        for field in self.private_fields:
            self.assertNotIn(field, response.data, field)

    def test_comment_create_forbidden(self):
        response = self.client.post(_location('comment-list'))
        self.assertEquals(response.status_code, 401)

    def test_comment_delete_forbidden(self):
        response = self.client.delete(_location('comment-detail', pk=1))
        self.assertEquals(response.status_code, 401)


class CommentTest(APITestCase):
    fixtures = ['patron', 'address', 'category', 'product', 'booking', 'comment']

    def setUp(self):
        self.model = get_model('rent', 'comment')
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')

    def test_comment_create_no_fields(self):
        response = self.client.post(_location('comment-list'))
        self.assertEquals(response.status_code, 400, response.data)

        required_fields = {'booking', 'rate', 'comment', 'author'}
        default_fields = {'author'}
        for field in required_fields - default_fields:
            self.assertIn(field, response.data['errors'], response.data)

    def test_comment_create_negative_rate(self):
        response = self.client.post(_location('comment-list'), {
            'rate': -5,
            'comment': "Comment",
            'booking': _location('booking-detail', pk='87ee8e9dec1d47c29ebb27e09bda8fc3'),
        })
        self.assertEquals(response.status_code, 400, response.data)
        self.assertIn('rate', response.data['errors'], response.data)

    def test_comment_create_large_rate(self):
        response = self.client.post(_location('comment-list'), {
            'rate': 15,
            'comment': "Comment",
            'booking': _location('booking-detail', pk='87ee8e9dec1d47c29ebb27e09bda8fc3'),
        })
        self.assertEquals(response.status_code, 400, response.data)
        self.assertIn('rate', response.data['errors'], response.data)

    def test_comment_create_not_mine_owner(self):
        response = self.client.post(_location('comment-list'), {
            'rate': 5,
            'comment': "Comment",
            'author': _location('patron-detail', pk=4),
            'booking': _location('booking-detail', pk='87ee8e9dec1d47c29ebb27e09bda8fc3'),
        })
        self.assertEquals(response.status_code, 201, response.data)
        # Location header must be properly set to redirect to the resource have just been created
        self.assertIn('Location', response)
        self.assertTrue(response['Location'].endswith(_location('comment-detail', pk=response.data['id'])))

        for k in ('created_at', 'author', 'rate', 'comment', 'booking', 'id'):
            self.assertIn(k, response.data, response.data)
            self.assertTrue(response.data[k], response.data)

        comment = self.model.objects.get(pk=response.data['id'])
        self.assertEqual(comment.type, COMMENT_TYPE_CHOICES.OWNER)
        self.assertEqual(comment.author.id, 1)

    def test_comment_create_partner_owner(self):
        response = self.client.post(_location('comment-list'), {
            'rate': 5,
            'comment': "Comment",
            'author': _location('patron-detail', pk=2),
            'booking': _location('booking-detail', pk='87ee8e9dec1d47c29ebb27e09bda8fc3'),
        })
        self.assertEquals(response.status_code, 201, response.data)
        # Location header must be properly set to redirect to the resource have just been created
        self.assertIn('Location', response)
        self.assertTrue(response['Location'].endswith(_location('comment-detail', pk=response.data['id'])))

        for k in ('created_at', 'author', 'rate', 'comment', 'booking', 'id'):
            self.assertIn(k, response.data, response.data)
            self.assertTrue(response.data[k], response.data)

        comment = self.model.objects.get(pk=response.data['id'])
        self.assertEqual(comment.type, COMMENT_TYPE_CHOICES.OWNER)
        self.assertEqual(comment.author.id, 1)

    def test_comment_create_owner(self):
        response = self.client.post(_location('comment-list'), {
             'rate': 5,
             'comment': "J'ai pu poser mes questions avec des r\u00e9ponses rapides et pr\u00e9cises, propri\u00e9taire sympathique, je recommande",
             'booking': _location('booking-detail', pk='87ee8e9dec1d47c29ebb27e09bda8fc3'),
        })
        self.assertEquals(response.status_code, 201, response.data)
        # Location header must be properly set to redirect to the resource have just been created
        self.assertIn('Location', response)
        self.assertTrue(response['Location'].endswith(_location('comment-detail', pk=response.data['id'])))

        for k in ('created_at', 'author', 'rate', 'comment', 'booking', 'id'):
            self.assertIn(k, response.data, response.data)
            self.assertTrue(response.data[k], response.data)

        Comment = get_model('rent', 'comment')
        c = Comment.objects.get(pk=response.data['id'])
        self.assertEquals(c.type, COMMENT_TYPE_CHOICES.OWNER)
        self.assertEqual(c.author.id, 1)

    def test_comment_create_not_mine_borrower(self):
        response = self.client.post(_location('comment-list'), {
            'rate': 5,
            'comment': "Comment",
            'author': _location('patron-detail', pk=4),
            'booking': _location('booking-detail', pk='8fd2f3df67e2488496899aeb22601b15'),
        })
        self.assertEquals(response.status_code, 201, response.data)
        # Location header must be properly set to redirect to the resource have just been created
        self.assertIn('Location', response)
        self.assertTrue(response['Location'].endswith(_location('comment-detail', pk=response.data['id'])))

        for k in ('created_at', 'author', 'rate', 'comment', 'booking', 'id'):
            self.assertIn(k, response.data, response.data)
            self.assertTrue(response.data[k], response.data)

        comment = self.model.objects.get(pk=response.data['id'])
        self.assertEqual(comment.type, COMMENT_TYPE_CHOICES.BORROWER)
        self.assertEqual(comment.author.id, 1)

    def test_comment_create_partner_borrower(self):
        response = self.client.post(_location('comment-list'), {
            'rate': 5,
            'comment': "Comment",
            'author': _location('patron-detail', pk=2),
            'booking': _location('booking-detail', pk='8fd2f3df67e2488496899aeb22601b15'),
        })
        self.assertEquals(response.status_code, 201, response.data)
        # Location header must be properly set to redirect to the resource have just been created
        self.assertIn('Location', response)
        self.assertTrue(response['Location'].endswith(_location('comment-detail', pk=response.data['id'])))

        for k in ('created_at', 'author', 'rate', 'comment', 'booking', 'id'):
            self.assertIn(k, response.data, response.data)
            self.assertTrue(response.data[k], response.data)

        comment = self.model.objects.get(pk=response.data['id'])
        self.assertEqual(comment.type, COMMENT_TYPE_CHOICES.BORROWER)
        self.assertEqual(comment.author.id, 1)

    def test_comment_create_not_mine_booking(self):
        response = self.client.post(_location('comment-list'), {
            'rate': 5,
            'comment': "Comment",
            'booking': _location('booking-detail', pk='349ce9ba628abfdfc9cb3a72608dab68'),
        })
        self.assertEquals(response.status_code, 400, response.data)

    def test_comment_create_borrower(self):
        response = self.client.post(_location('comment-list'), {
             'rate': 5,
             'comment': "J'ai pu poser mes questions avec des r\u00e9ponses rapides et pr\u00e9cises, propri\u00e9taire sympathique, je recommande",
             'booking': _location('booking-detail', pk='8fd2f3df67e2488496899aeb22601b15'),
        })
        self.assertEquals(response.status_code, 201, response.data)
        # Location header must be properly set to redirect to the resource have just been created
        self.assertIn('Location', response)
        self.assertTrue(response['Location'].endswith(_location('comment-detail', pk=response.data['id'])))

        for k in ('created_at', 'author', 'rate', 'comment', 'booking', 'id'):
            self.assertIn(k, response.data, response.data)
            self.assertTrue(response.data[k], response.data)

        Comment = get_model('rent', 'comment')
        c = Comment.objects.get(pk=response.data['id'])
        self.assertEqual(c.type, COMMENT_TYPE_CHOICES.BORROWER)
        self.assertEqual(c.author.id, 1)

    def test_comment_list(self):
        response = self.client.get(_location('comment-list'))
        self.assertEquals(response.status_code, 200, response.data)
        # check pagination data format in the response
        expected = {
            'count': 2, # we should get 2 comments
            'previous': None,
            'next': None,
        }
        self.assertDictContainsSubset(expected, response.data)
        self.assertIn('results', response.data)
        # check data
        self.assertEquals(response.data['count'], len(response.data['results']))

    def test_comment_get_by_id(self):
        response = self.client.get(_location('comment-detail', pk=1))
        self.assertEquals(response.status_code, 200, response.data)

    def test_comment_get_author_owner(self):
        response = self.client.get(_location('comment-detail', pk=1))
        self.assertEquals(response.status_code, 200, response.data)
        self.assertIn('author', response.data, response.data)
        self.assertTrue(response.data['author'].endswith(_location('patron-detail', pk=2)))

    def test_comment_get_author_borrower(self):
        response = self.client.get(_location('comment-detail', pk=2))
        self.assertEquals(response.status_code, 200, response.data)
        self.assertIn('author', response.data, response.data)
        self.assertTrue(response.data['author'].endswith(_location('patron-detail', pk=1)))

    def test_comment_delete(self):
        Comment = get_model('rent', 'Comment')
        self.assertEquals(Comment.objects.filter(pk=1).count(), 1)
        response = self.client.delete(_location('comment-detail', pk=1))
        self.assertEquals(response.status_code, 204, response.data)
        self.assertEquals(Comment.objects.filter(pk=1).count(), 0)

    def test_ordering(self):
        response = self.client.get(_location('comment-list'), {'ordering': 'created_at'})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEqual(
            response.data['results'],
            sorted(response.data['results'], key=itemgetter('created_at')))

    def test_reverse_ordering(self):
        response = self.client.get(_location('comment-list'), {'ordering': '-created_at'})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEqual(
            response.data['results'],
            sorted(response.data['results'], key=itemgetter('created_at'), reverse=True))

    def test_filter1(self):
        response = self.client.get(_location('comment-list'), {'rate': 5})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertGreater(response.data['count'], 0)
        self.assertEqual(response.data['results'], filter(lambda x: x['rate'] == 5, response.data['results']))
        self.assertEqual([], filter(lambda x: x['rate'] != 5, response.data['results']))

    def test_filter2(self):
        response = self.client.get(_location('comment-list'), {'rate': 4})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['results'], filter(lambda x: x['rate'] == 4, response.data['results']))
        self.assertEqual([], filter(lambda x: x['rate'] != 4, response.data['results']))


class StaffCommentTest(APITestCase):
    fixtures = ['patron_staff', 'address', 'category', 'product', 'booking', 'comment']

    def setUp(self):
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')

    def test_ordering(self):
        response = self.client.get(_location('comment-list'), {'ordering': 'created_at'})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEqual(
            response.data['results'],
            sorted(response.data['results'], key=itemgetter('created_at')))

    def test_reverse_ordering(self):
        response = self.client.get(_location('comment-list'), {'ordering': '-created_at'})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEqual(
            response.data['results'],
            sorted(response.data['results'], key=itemgetter('created_at'), reverse=True))

    def test_filter1(self):
        response = self.client.get(_location('comment-list'), {'rate': 5})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertGreater(response.data['count'], 0)
        self.assertEqual(response.data['results'], filter(lambda x: x['rate'] == 5, response.data['results']))
        self.assertEqual([], filter(lambda x: x['rate'] != 5, response.data['results']))

    def test_filter2(self):
        response = self.client.get(_location('comment-list'), {'rate': 4})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['results'], filter(lambda x: x['rate'] == 4, response.data['results']))
        self.assertEqual([], filter(lambda x: x['rate'] != 4, response.data['results']))


class AnonymousSinisterTest(APITestCase):

    fixtures = ['patron', 'address', 'category', 'product', 'booking', 'sinister']

    def test_sinister_list_forbidden(self):
        response = self.client.get(_location('sinister-list'))
        self.assertEquals(response.status_code, 401)

    def test_sinister_show_forbidden(self):
        response = self.client.get(_location('sinister-detail', pk='aaf26618b6654a05bf3cc57ade322928'))
        self.assertEquals(response.status_code, 401)

    def test_sinister_create_forbidden(self):
        response = self.client.post(_location('sinister-list'))
        self.assertEquals(response.status_code, 401)


class SinisterTest(APITestCase):

    fixtures = ['patron', 'address', 'category', 'product', 'booking', 'sinister']

    def setUp(self):
        self.model = get_model('rent', 'Sinister')
        self.client.login(username='alexandre.woog@e-loue.com', password='alexandre')

    def test_sinister_create_no_fields(self):
        response = self.client.post(_location('sinister-list'))
        self.assertEquals(response.status_code, 400, response.data)

        required_fields = {'booking', 'product', 'description', 'author'}
        default_fields = {'author'}
        for field in required_fields - default_fields:
            self.assertIn(field, response.data['errors'], response.data)

    def test_sinister_create_product_from_wrong_booking(self):
        response = self.client.post(_location('sinister-list'), {
            'product': _location('product-detail', pk=2),
            'patron': _location('patron-detail', pk=1),
            'booking': _location('booking-detail', pk='87ee8e9dec1d47c29ebb27e09bda8fc3'),
            'description': 'Description'
        })

        self.assertEquals(response.status_code, 400, response.data)
        self.assertIn('product', response.data['errors'], response.data)

    def test_sinister_create_not_mine_booking(self):
        response = self.client.post(_location('sinister-list'), {
            'product': _location('product-detail', pk=6),
            'patron': _location('patron-detail', pk=1),
            'booking': _location('booking-detail', pk='349ce9ba628abfdfc9cb3a72608dab68'),
            'description': 'Description'
        })
        self.assertEquals(response.status_code, 400, response.data)
        self.assertIn('booking', response.data['errors'], response.data)

    def test_sinister_create_not_mine(self):
        response = self.client.post(_location('sinister-list'), {
            'product': _location('product-detail', pk=1),
            'patron': _location('patron-detail', pk=2),
            'booking': _location('booking-detail', pk='87ee8e9dec1d47c29ebb27e09bda8fc3'),
            'description': 'Description'
        })

        self.assertEquals(response.status_code, 201, response.data)

        self.assertIn('uuid', response.data)
        self.assertIn('Location', response)
        self.assertTrue(response['Location'].endswith(_location('sinister-detail', pk=response.data['uuid'])))

        sinister = self.model.objects.get(pk=response.data['uuid'])
        self.assertEqual(sinister.product_id, 1)
        self.assertEqual(sinister.patron_id, 1)
        self.assertEqual(sinister.booking_id, '87ee8e9dec1d47c29ebb27e09bda8fc3')
        self.assertEqual(sinister.description, 'Description')

    def test_sinister_create(self):
        response = self.client.post(_location('sinister-list'), {
            'product': _location('product-detail', pk=1),
            'patron': _location('patron-detail', pk=1),
            'booking': _location('booking-detail', pk='87ee8e9dec1d47c29ebb27e09bda8fc3'),
            'description': 'Description'
        })

        self.assertEquals(response.status_code, 201, response.data)

        self.assertIn('uuid', response.data)
        self.assertIn('Location', response)
        self.assertTrue(response['Location'].endswith(_location('sinister-detail', pk=response.data['uuid'])))

        sinister = self.model.objects.get(pk=response.data['uuid'])
        self.assertEqual(sinister.product_id, 1)
        self.assertEqual(sinister.patron_id, 1)
        self.assertEqual(sinister.booking_id, '87ee8e9dec1d47c29ebb27e09bda8fc3')
        self.assertEqual(sinister.description, 'Description')

    def test_sinister_get_by_id(self):
        response = self.client.get(_location('sinister-detail', pk='aaf26618b6654a05bf3cc57ade322928'))
        self.assertEquals(response.status_code, 200, response.data)

    def test_sinister_list_paginated(self):
        response = self.client.get(_location('sinister-list'))
        self.assertEquals(response.status_code, 200, response.data)
        # check pagination data format in the response
        expected = {
            'count': 2,
            'previous': None,
            'next': None
        }
        self.assertDictContainsSubset(expected, response.data)
        self.assertIn('results', response.data)
        # check data
        self.assertEquals(response.data['count'], len(response.data['results']))

    def test_filter1(self):
        response = self.client.get(_location('sinister-list'), {'booking': 'a72608d9a7e349ce9ba628abfdfc9cb3'})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertGreater(response.data['count'], 0)
        self.assertEqual(
            response.data['results'],
            filter(lambda x: x['booking'].endswith(_location('booking-detail', pk='a72608d9-a7e3-49ce-9ba6-28abfdfc9cb3')), response.data['results']))
        self.assertEqual(
            [],
            filter(lambda x: not x['booking'].endswith(_location('booking-detail', pk='a72608d9-a7e3-49ce-9ba6-28abfdfc9cb3')), response.data['results']))

    def test_filter2(self):
        response = self.client.get(_location('sinister-list'), {'booking': '349ce9ba628abfdfc9cb3a72608d9a7e'})
        self.assertEquals(response.status_code, 200, response.data)
        self.assertGreater(response.data['count'], 0)
        self.assertEqual(
            response.data['results'],
            filter(lambda x: x['booking'].endswith(_location('booking-detail', pk='349ce9ba-628a-bfdf-c9cb-3a72608d9a7e')), response.data['results']))
        self.assertEqual(
            [],
            filter(lambda x: not x['booking'].endswith(_location('booking-detail', pk='349ce9ba-628a-bfdf-c9cb-3a72608d9a7e')), response.data['results']))
