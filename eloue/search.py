# -*- coding: utf-8 -*-

from django.db import models
from queued_search.signals import QueuedSignalProcessor


class HaystackSignalProcessor(QueuedSignalProcessor):
    #senders = (Patron, Alert, Product, CarProduct, RealEstateProduct)
    _SENDER_MAP = {
        'Booking': 'product',
        'UnavailabilityPeriod': 'product',
    }

    def setup(self):
        post_save = models.signals.post_save
        post_delete = models.signals.post_delete

        post_save.connect(self.enqueue_save)
        post_delete.connect(self.enqueue_delete)

    def teardown(self):
        post_save = models.signals.post_save
        post_delete = models.signals.post_delete

        post_save.disconnect(self.enqueue_save)
        post_delete.disconnect(self.enqueue_delete)

    def enqueue_save(self, sender, instance, **kwargs):
        if sender.__name__ in self._SENDER_MAP:
            instance = getattr(instance, self._SENDER_MAP[sender.__name__], instance)
        return self.enqueue('update', instance)

    def enqueue_delete(self, sender, instance, **kwargs):
        if sender.__name__ in self._SENDER_MAP:
            instance = getattr(instance, self._SENDER_MAP[sender.__name__], instance)
        return self.enqueue('delete', instance)
