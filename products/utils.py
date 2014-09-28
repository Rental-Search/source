# -*- coding: utf-8 -*-
from copy import deepcopy

from django.utils.text import wrap
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property
from django.utils import six

from eloue.utils import Enum


def format_quote(sender, body):
    """
    Wraps text at 55 chars and prepends each
    line with `> `.
    Used for quoting messages in replies.
    """
    lines = wrap(body, 55).split('\n')
    for i, line in enumerate(lines):
        lines[i] = "> %s" % line
    quote = '\n'.join(lines)
    return _(u"\n\n\n\n\n%(sender)s wrote:\n%(body)s") % {
        'sender': sender,
        'body': quote,
        }
            
def escape_percent_sign(unescaped_url):
    """
    Escapes standalone percent signs in raw url's, like localhost:8000/location/jardinage?q=ch%C3%A8vre&sort=price
    """
    return unescaped_url.replace('%', '%%')


class UnitEnum(Enum):
    """
    A special Enum version for UNIT (see products/choices.py).
    """
    def __init__(self, enum_list):
        super(UnitEnum, self).__init__(enum_list)
        self.enum_dict_prefixed = {item[0]: item[3] for item in enum_list}
        self._day_amount_dict = {item[0]: item[4] for item in enum_list}
        self._package_dict = {item[0]: item[5] for item in enum_list}

    def __deepcopy__(self, memo={}):
        copy = super(UnitEnum, self).__deepcopy__(memo=memo)
        copy.enum_dict_prefixed = deepcopy(self.enum_dict_prefixed, memo=memo)
        copy._day_amount_dict = deepcopy(self._day_amount_dict)
        copy._package_dict = deepcopy(self._package_dict)
        return copy

    def items(self):
        return six.iteritems(self.enum_dict)

    @property
    def prefixed(self):
        return self.enum_dict_prefixed

    @cached_property
    def reverted(self):
        return dict(six.moves.zip(six.itervalues(self.enum_dict), six.iterkeys(self.enum_dict)))

    @property
    def units(self):
        return self._day_amount_dict

    @property
    def package(self):
        return self._package_dict
