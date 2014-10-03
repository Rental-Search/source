# -*- coding: utf-8 -*-
import itertools
from eloue.api.permissions import AllowPublicRetrieve


def allow_anonymous_retrieve(cls):
    """Decorator that add to ViewSet ability of getting objects anonymously."""
    cls.permission_classes = tuple(
        itertools.chain((AllowPublicRetrieve,), cls.permission_classes))
    return cls
