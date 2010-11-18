# -*- coding: utf-8 -*-
from django.utils.hashcompat import md5_constructor
from django.utils.http import urlquote


def cache_key(fragment_name, *args):
    hasher = md5_constructor(u':'.join([urlquote(arg) for arg in args]))
    return 'template.cache.%s.%s' % (fragment_name, hasher.hexdigest())
