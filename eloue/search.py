
from django.db.models.signals import post_save, post_delete

from queued_search.signals import QueuedSignalProcessor

from accounts.models import Patron
from products.models import (
    Alert, Product, CarProduct,
    RealEstateProduct, UnavailabilityPeriod
)
from rent.models import Booking

class HaystackSignalProcessor(QueuedSignalProcessor):
    senders = (Patron, Alert, Product, CarProduct, RealEstateProduct)
    related_senders = (Booking, UnavailabilityPeriod)

    def setup(self):
        for sender in self.senders:
            post_save.connect(self.enqueue_save, sender=sender)
            post_delete.connect(self.enqueue_delete, sender=sender)

        # If booking or UnavailabilityPeriod was changed - update ProductIndex 
        for sender in self.related_senders:
            post_save.connect(self.enqueue_related_save, sender=sender)
            post_delete.connect(self.enqueue_related_delete, sender=sender)

    def teardown(self):
        for sender in self.senders:
            post_save.disconnect(self.enqueue_save, sender=sender)
            post_delete.disconnect(self.enqueue_delete, sender=sender)

        for sender in self.related_senders:
            post_save.disconnect(self.enqueue_related_save, sender=sender)
            post_delete.disconnect(self.enqueue_related_delete, sender=sender)

    def enqueue_related_save(self, sender, instance, **kwargs):
        print "enqueue_related_save", instance
        return self.enqueue('update', instance.product)

    def enqueue_related_delete(self, sender, instance, **kwargs):
        print "enqueue_related_delete", instance
        return self.enqueue('delete', instance.product)
