
from django.db.models.signals import post_save, post_delete

from queued_search.signals import QueuedSignalProcessor

from accounts.models import Patron
from products.models import Alert, Product, CarProduct, RealEstateProduct

class HaystackSignalProcessor(QueuedSignalProcessor):
    senders = (Patron, Alert, Product, CarProduct, RealEstateProduct)

    def setup(self):
        for sender in self.senders:
            post_save.connect(self.enqueue_save, sender=sender)
            post_delete.connect(self.enqueue_delete, sender=sender)

    def teardown(self):
        for sender in self.senders:
            post_save.disconnect(self.enqueue_save, sender=sender)
            post_delete.disconnect(self.enqueue_delete, sender=sender)
