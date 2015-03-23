# coding=utf-8
from itertools import groupby, chain
import operator
from eloue.utils import itertools_accumulate
from products.models import UnavailabilityPeriod
from rent.models import Booking
from rent.choices import BOOKING_STATE


BOOKED_STATE = (
    BOOKING_STATE.PENDING,
    BOOKING_STATE.ONGOING,
)


# TODO There is an obsolete version in rent.Booking.calculate_available_quantity
def __get_unavailable_periods(product, started_at, ended_at=None):
    bookings = Booking.objects.filter(
        product=product, state__in=BOOKED_STATE,
        ended_at__gt=started_at)
    unavailabilities = UnavailabilityPeriod.objects.filter(
        product=product,
        ended_at__gt=started_at)

    if ended_at is not None:
        bookings = bookings.filter(started_at__lt=ended_at)
        unavailabilities = unavailabilities.filter(
            started_at__lt=ended_at)

    bookings = bookings.values_list(
        'started_at', 'ended_at', 'quantity')
    unavailabilities = unavailabilities.values_list(
        'started_at', 'ended_at', 'quantity')

    periods_tuple = chain(bookings, unavailabilities)
    return groupby(sorted(chain.from_iterable(
        ((start, 1, value), (end, -1, value)) for start, end, value in periods_tuple),
        key=operator.itemgetter(0)),
        key=operator.itemgetter(0)
    )


def get_unavailable_periods(product, started_at, ended_at=None, quantity=1):
    """Returns unavailable periods between dates started_at and ended_at."""
    available_quantity = product.quantity
    if quantity > available_quantity:
        return ([], [])

    grouped_dates = __get_unavailable_periods(
            product, started_at, ended_at=ended_at)
    starts, ends, new_period = [], [], None

    """
    In [47]: product.quantity
    Out[47]: 2
    In [48]: periods_tuple  # (start, stop, quantity)
    Out[48]: [
    (datetime.datetime(2015, 2, 1, 8, 0), datetime.datetime(2015, 2, 6, 9, 0), 1),
    (datetime.datetime(2015, 2, 3, 10, 0), datetime.datetime(2015, 2, 5, 11, 0), 1),
    (datetime.datetime(2015, 1, 29, 8, 0), datetime.datetime(2015, 1, 31, 9, 0), 1)]

    In [60]: for key, val in grouped_dates:
    print key, list(val)
    #       key,    list of (date, 1 = start booking / -1 = stop booking, quantity)
    ....:
    2015-01-29 08:00:00 [(datetime.datetime(2015, 1, 29, 8, 0), 1, 1)]
    2015-01-31 09:00:00 [(datetime.datetime(2015, 1, 31, 9, 0), -1, 1)]
    2015-02-01 08:00:00 [(datetime.datetime(2015, 2, 1, 8, 0), 1, 1)]
    2015-02-03 10:00:00 [(datetime.datetime(2015, 2, 3, 10, 0), 1, 1)]
    2015-02-05 11:00:00 [(datetime.datetime(2015, 2, 5, 11, 0), -1, 1)]
    2015-02-06 09:00:00 [(datetime.datetime(2015, 2, 6, 9, 0), -1, 1)]

    """
    for key, val in grouped_dates:
        # calculate available items of product for current date
        available_quantity -= sum(map(lambda x: operator.mul(*operator.itemgetter(1, 2)(x)), val))

        if available_quantity < quantity:
            # start new unavailable period
            if not new_period: new_period = key
        else:
            if new_period:
                # stop current unavailable period
                starts.append(new_period)
                ends.append(key)
                new_period = None

    return (starts, ends)


def calculate_available_quantity(product, started_at, ended_at):
    """Returns maximal available quantity between dates started_at and ended_at."""
    grouped_dates = __get_unavailable_periods(product, started_at, ended_at)
    sum_gen = (sum(map(lambda x: operator.mul(*operator.itemgetter(1, 2)(x)), j)) for i, j in grouped_dates)
    return product.quantity - max(itertools_accumulate(sum_gen, start=0))
