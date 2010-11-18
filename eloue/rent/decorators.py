# -*- coding: utf-8 -*-
from django.db import connection
from django.http import HttpResponseForbidden


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


def ownership_required(model, object_key='object_id', ownership=None):
    def wrapper(view_func):
        def inner_wrapper(request, *args, **kwargs):
            user = request.user
            grant = False
            object_id = kwargs.get(object_key, None)
            if object_id:
                names = [(rel.get_accessor_name(), rel.field.name) for rel in user._meta.get_all_related_objects() if rel.model == model]
                if ownership:
                    names = filter(lambda name: name[1] in ownership, names)
                names = map(lambda name: getattr(user, name[0]).filter(pk=object_id).exists(), names)
                if names:
                    grant = any(names)
            if not grant:
                return HttpResponseForbidden()
            return view_func(request, *args, **kwargs)
        return inner_wrapper
    return wrapper
