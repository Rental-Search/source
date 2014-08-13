
from itertools import chain

from django import template

from pyjade.runtime import is_mapping, is_iterable, get_cardinality

register = template.Library()

def iteration(obj, num_keys):
    """
    Jade iteration supports "for 'value' [, key]?" iteration only.
    PyJade has implicitly supported value unpacking instead, without
    the list indexes. Trying to not break existing code, the following
    rules are applied:

      1. If the object is a mapping type, return it as-is, and assume
         the caller has the correct set of keys defined.

      2. If the object's values are iterable (and not string-like):
         a. If the number of keys matches the cardinality of the object's
            values, return the object as-is.
         b. If the number of keys is one more than the cardinality of
            values, return a list of [v(0), v(1), ... v(n), index]

      3. Else the object's values are not iterable, or are string like:
         a. if there's only one key, return the list
         b. otherwise return a list of (value,index) tuples

    """

    # If the object is a mapping type, return it as-is
    if is_mapping(obj):
        return obj

    _marker = []

    iter_obj = iter(obj)
    head = next(iter_obj, _marker)
    iter_obj = chain([head], iter_obj)

    if head is _marker:
        # Empty list
        return []

    if is_iterable(head) and not is_mapping(head):
        if num_keys == get_cardinality(head) + 1:
            return (tuple(item) + (ix,) for ix, item in enumerate(iter_obj))
        else:
            return iter_obj

    elif num_keys == 2:
        return ((item, ix) for ix, item in enumerate(iter_obj))

    else:
        return iter_obj

register.filter('__pyjade_iter', iteration)
