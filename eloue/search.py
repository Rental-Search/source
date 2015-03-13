# -*- coding: utf-8 -*-

from django.db import models
from queued_search.signals import QueuedSignalProcessor


class HaystackSignalProcessor(QueuedSignalProcessor):
    #senders = (Patron, Alert, Product, CarProduct, RealEstateProduct)
    related_senders = (('rent', 'Booking'), ('products', 'UnavailabilityPeriod'))

    def setup(self):
        post_save = models.signals.post_save
        post_delete = models.signals.post_delete

        post_save.connect(self.enqueue_save)
        post_delete.connect(self.enqueue_delete)

        # If booking or UnavailabilityPeriod was changed - update ProductIndex
        for app, model in self.related_senders:
            sender = models.loading.get_model(app, model)
            post_save.connect(
                    self.enqueue_product_related_save, sender=sender)
            post_delete.connect(
                    self.enqueue_product_related_delete, sender=sender)

    def teardown(self):
        post_save = models.signals.post_save
        post_delete = models.signals.post_delete

        post_save.disconnect(self.enqueue_save)
        post_delete.disconnect(self.enqueue_delete)

        for app, model in self.related_senders:
            sender = models.loading.get_model(app, model)
            post_save.disconnect(
                    self.enqueue_product_related_save, sender=sender)
            post_delete.disconnect(
                    self.enqueue_product_related_delete, sender=sender)

    def enqueue_product_related_save(self, sender, instance, **kwargs):
        return self.enqueue('update', instance.product)

    def enqueue_product_related_delete(self, sender, instance, **kwargs):
        return self.enqueue('delete', instance.product)
