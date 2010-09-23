# -*- coding: utf-8 -*-
import re
import inspect

from freshen.checks import *
from django.test.testcases import TransactionTestCase


__all__ = ['ok_', 'eq_', 'make_decorator', 'raises', 'set_trace', 'timed',
            'with_setup', 'TimeExpired', 'istest', 'nottest']

# Expose assert from django TestCase
caps = re.compile('([A-Z])')

def pep8(name):
    return caps.sub(lambda m: '_' + m.groups()[0].lower(), name)

class Dummy(TransactionTestCase):
    def nop():
        pass

_t = Dummy('nop')

for at in [ at for at in dir(_t)
            if (at.startswith('assert') or at.startswith('fail')) and not '_' in at and inspect.ismethod(getattr(_t, at)) ]:
    pepd = pep8(at)
    vars()[pepd] = getattr(_t, at)
    __all__.append(pepd)

del Dummy
del _t
del pep8
