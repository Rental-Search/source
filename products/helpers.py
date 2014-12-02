# coding=utf-8
from itertools import groupby, chain
import operator
from eloue.utils import itertools_accumulate
from products.models import UnavailabilityPeriod
from rent.models import Booking


def max_occupied_quantity(periods):
    periods_tuple = ((period.started_at, period.ended_at, period.quantity) for period in periods)
    grouped_dates = groupby(sorted(chain.from_iterable(
        ((start, 1, value), (end, -1, value)) for start, end, value in periods_tuple),
        key=operator.itemgetter(0)),
        key=operator.itemgetter(0)
    )
    sum_gen = (sum(map(lambda x: operator.mul(*operator.itemgetter(1, 2)(x)), j)) for i, j in grouped_dates)
    return max(itertools_accumulate(sum_gen, start=0))


def calculate_available_quantity(product, started_at, ended_at):
    """Returns maximal available quantity between dates started_at and ended_at."""

    bookings = Booking.objects.filter(
        product=product, state__in=["pending", "ongoing"], ended_at__gt=started_at, started_at__lt=ended_at)
    unavailability_periods = UnavailabilityPeriod.objects.filter(
        product=product, started_at=started_at, ended_at=ended_at)

    return product.quantity - max_occupied_quantity(chain(bookings, unavailability_periods))
