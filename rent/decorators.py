# -*- coding: utf-8 -*-
from django.db import connection


def incr_sequence(field, sequence_name):
    def wrapper(view_func):
        def inner_wrapper(self, *args, **kwargs):
            if not getattr(self, field):
                cursor = connection.cursor()
                cursor.execute("SELECT nextval(%s)", [sequence_name])
                row = cursor.fetchone()
                setattr(self, field, row[0])
            return view_func(self, *args, **kwargs)
        return inner_wrapper
    return wrapper
