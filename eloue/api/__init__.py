# -*- coding: utf-8 -*-

from django.db import connection
from django.db.models.signals import class_prepared
from django.dispatch import receiver


@receiver(class_prepared)
def setup_postgres_intarray(sender, **kwargs):
    """
    Always create PostgreSQL intarray extension if it doesn't already exist
    on the database before syncing the database.
    Requires PostgreSQL 9.1 or newer.
    """
    if sender.__name__ == 'Product':
        cursor = connection.cursor()
        cursor.execute("CREATE EXTENSION IF NOT EXISTS intarray")
