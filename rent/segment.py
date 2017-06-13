import datetime
import analytics
from django.conf import settings

# Ref Segment Document for Python
# https://segment.com/docs/libraries/python/

analytics.write_key = settings.ANALYTICS_WRITE_KEY

class BookingSegment(object):
      def __init__(self, arg):
            super(BookingSegment, self).__init__()
            self.booking = arg
            self.owner_id = self.booking.owner.id
            self.borrower_id = self.booking.borrower.id

	# Identify in segment allows use other actions
      def identify(self, user_id):
		analytics.identify(user_id, {
			'last_login': datetime.datetime.now()
			})

      def send_booking_accepted_received_track(self):
		self.identify(self.borrower_id)
		analytics.track(self.borrower_id, 'Booking Accepted Received', {
		'booking id': self.booking.uuid,
		'borrower id': self.booking.borrower.id,
		'owner id': self.booking.owner.id,
            'category': self.booking.product.category.name,
            'category slug': self.booking.product.category.slug,
            'product id': self.booking.product.id,
            'product summary': self.booking.product.summary,
            'product pictures': self.booking.product.pictures.count(),
            'duration': self.booking.started_at - self.booking.ended_at,
            'start date': self.booking.started_at,
            'end date': self.booking.ended_at,
            'state': self.booking.state,
            'total amount': str(self.booking.total_amount)
			})

      def send_booking_noanswered_track(self):
		self.identify(self.owner_id)
		analytics.track(self.owner_id, 'Booking NoAnswered', {
		'booking id': self.booking.uuid,
		'borrower id': self.booking.borrower.id,
		'owner id': self.booking.owner.id,
            'category': self.booking.product.category.name,
            'category slug': self.booking.product.category.slug,
            'product id': self.booking.product.id,
            'product summary': self.booking.product.summary,
            'product pictures': self.booking.product.pictures.count(),
            'duration': self.booking.started_at - self.booking.ended_at,
            'start date': self.booking.started_at,
            'end date': self.booking.ended_at,
            'state': self.booking.state,
            'total amount': str(self.booking.total_amount)
			})
      
      def send_booking_authorazing_track(self):
		self.identify(self.borrower_id)
		analytics.track(self.borrower_id, 'Booking Authorazing', {
		'booking id': self.booking.uuid,
		'borrower id': self.booking.borrower.id,
		'owner id': self.booking.owner.id,
            'category': self.booking.product.category.name,
            'category slug': self.booking.product.category.slug,
            'product id': self.booking.product.id,
            'product summary': self.booking.product.summary,
            'product pictures': self.booking.product.pictures.count(),
            'duration': self.booking.started_at - self.booking.ended_at,
            'start date': self.booking.started_at,
            'end date': self.booking.ended_at,
            'state': self.booking.state,
            'total amount': str(self.booking.total_amount)
			})

      def send_booking_rejected_received_track(self):
		self.identify(self.borrower_id)
		analytics.track(self.borrower_id, 'Booking Rejected Received', {
		'booking id': self.booking.uuid,
		'borrower id': self.booking.borrower.id,
		'owner id': self.booking.owner.id,
            'category': self.booking.product.category.name,
            'category slug': self.booking.product.category.slug,
            'product id': self.booking.product.id,
            'product summary': self.booking.product.summary,
            'product pictures': self.booking.product.pictures.count(),
            'duration': self.booking.started_at - self.booking.ended_at,
            'start date': self.booking.started_at,
            'end date': self.booking.ended_at,
            'state': self.booking.state,
            'total amount': str(self.booking.total_amount)
			})

      def send_booking_canceled_received_track(self):
		self.identify(self.owner_id)
		analytics.track(self.owner_id, 'Booking Canceled Received', {
		'booking id': self.booking.uuid,
		'borrower id': self.booking.borrower.id,
		'owner id': self.booking.owner.id,
            'category': self.booking.product.category.name,
            'category slug': self.booking.product.category.slug,
            'product id': self.booking.product.id,
            'product summary': self.booking.product.summary,
            'product pictures': self.booking.product.pictures.count(),
            'duration': self.booking.started_at - self.booking.ended_at,
            'start date': self.booking.started_at,
            'end date': self.booking.ended_at,
            'state': self.booking.state,
            'total amount': str(self.booking.total_amount)
			})
      
      def send_booking_requested_received_track(self):
		self.identify(self.owner_id)
		analytics.track(self.owner_id, 'Booking Requested Received', {
		'booking id': self.booking.uuid,
		'borrower id': self.booking.borrower.id,
		'owner id': self.booking.owner.id,
            'category': self.booking.product.category.name,
            'category slug': self.booking.product.category.slug,
            'product id': self.booking.product.id,
            'product summary': self.booking.product.summary,
            'product pictures': self.booking.product.pictures.count(),
            'duration': self.booking.started_at - self.booking.ended_at,
            'start date': self.booking.started_at,
            'end date': self.booking.ended_at,
            'state': self.booking.state,
            'total amount': str(self.booking.total_amount)
			})
