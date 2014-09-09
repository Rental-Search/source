# -*- coding: utf-8 -*-
import unittest
from datetime import datetime, timedelta
from calendar import monthrange, weekday
from copy import deepcopy
from decimal import Decimal as D
import os.path

from pyke import knowledge_engine

from django.utils.translation import ugettext_lazy as _
from django.utils.functional import LazyObject, cached_property
from django.utils import six

try:
    from eloue.utils import Enum
except ImportError:
    class Enum(object):
        """
        A small helper class for more readable enumerations,
        and compatible with Django's choice convention.
    
        >>> PERSON = Enum([
        ...   (100, 'NAME', 'Verbose name title'),
        ...   (200, 'AGE', 'Verbose age title')
        ... ])
        >>> PERSON.AGE
        200
        >>> PERSON[1]
        (200, 'Verbose age title')
        >>> PERSON['NAME']
        100
        >>> len(PERSON)
        2
        >>> (100, 'Verbose name title') in PERSON
        True
        """
        def __init__(self, enum_list):
            self.enum_list = [(item[0], item[2]) for item in enum_list]
            self.enum_dict = {item[1]: item[0] for item in enum_list}

        def __contains__(self, value):
            return value in self.enum_list

        def __len__(self):
            return len(self.enum_list)

        def __getitem__(self, value):
            if isinstance(value, basestring):
                return self.enum_dict[value]
            elif isinstance(value, int):
                return self.enum_list[value]

        def __getattr__(self, name):
            return self.enum_dict[name]

        def __iter__(self):
            return self.enum_list.__iter__()

        def __deepcopy__(self, memo={}):
            copy = self.__class__([])
            copy.enum_list = deepcopy(self.enum_list, memo=memo)
            copy.enum_dict = deepcopy(self.enum_dict, memo=memo)
            return copy

        def keys(self):
            return six.iterkeys(self.enum_dict)

        def values(self):
            return six.itervalues(self.enum_dict)

try:
    from products.utils import UnitEnum
except ImportError:
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
            return dict(zip(six.itervalues(self.enum_dict), six.iterkeys(self.enum_dict)))
   
        @property
        def units(self):
            return self._day_amount_dict
   
        @property
        def package(self):
            return self._package_dict

def _n_days(amount, delta, rounding=True):
    return amount * (delta.days + delta.seconds / D('86400'))

try:
    from products.choices import UNIT
except ImportError:
    def _noop(value, *args, **kwargs):
        return value

    UNIT = UnitEnum([
        (0, 'HOUR', _(u'heure'),
         _(u'1 heure'),
         _noop,
         lambda amount, delta, rounding=True: amount * (delta.seconds / D('3600')),
         ),
        (1, 'DAY', _(u'jour'),
         _(u'1 jour'),
         _noop,
         lambda amount, delta, rounding=True: amount * (max(delta.days + delta.seconds / D('86400'), 1) if rounding else delta.days + delta.seconds / D('86400')),
         ),
        (2, 'WEEK_END', _(u'week-end'),
         _(u'1 week-end'),
         _noop,
         _noop,
         ),
        (3, 'WEEK', _(u'semaine'),
         _(u'1 semaine'),
         lambda amount: amount / 7,
         _n_days,
         ),
        (4, 'TWO_WEEKS', _(u'deux semaines'),
         _(u'2 semaines'),
         lambda amount: amount / 14,
         _n_days,
         ),
        (5, 'MONTH', _(u'mois'),
         _(u'1 mois'),
         lambda amount: amount / 30,
         _n_days,
         ),
        (6, 'THREE_DAYS', _(u'3jours'),
         _(u'3 jours'),
         lambda amount: amount / 3,
         _n_days,
         ),
        (7, 'FIFTEEN_DAYS', _(u'15jours'),
         _(u'15 jours'),
         lambda amount: amount / 15,
         _n_days,
         ),
    ])

try:
    from products.choices import UNITS
except ImportError:
    UNITS = {
        0: lambda amount: amount,
        1: lambda amount: amount,
        2: lambda amount: amount,
        3: lambda amount: amount / 7,
        4: lambda amount: amount / 14,
        5: lambda amount: amount / 30,
        6: lambda amount: amount / 3,
        7: lambda amount: amount / 15,
    }

try:
    from rent.choices import PACKAGES_UNIT, PACKAGES
except ImportError:
    PACKAGES_UNIT = {
        'hour': UNIT.HOUR,
        'week_end': UNIT.WEEK_END,
        'day': UNIT.DAY,
        'week': UNIT.WEEK,
        'two_weeks': UNIT.TWO_WEEKS,
        'month': UNIT.MONTH,
        'three_days': UNIT.THREE_DAYS,
        'fifteen_days': UNIT.FIFTEEN_DAYS,
    }

    PACKAGES = {
        UNIT.HOUR: lambda amount, delta, rounding=True: amount * (delta.seconds / D('3600')),
        UNIT.WEEK_END: lambda amount, delta, rounding=True: amount,
        UNIT.DAY: lambda amount, delta, rounding=True: amount * (max(delta.days + delta.seconds / D('86400'), 1) if rounding else delta.days + delta.seconds / D('86400')),
        UNIT.WEEK: _n_days,
        UNIT.TWO_WEEKS: _n_days,
        UNIT.MONTH: _n_days,
        UNIT.THREE_DAYS: _n_days,
        UNIT.FIFTEEN_DAYS: _n_days,
    }

# -----------------------------------------------------------------------------
class TestUnitEnum(unittest.TestCase):
    def test_access(self):
        self.assertEqual(UNIT.WEEK, 3)
        self.assertEqual(UNIT[3], (3, _(u'semaine')))
        self.assertEqual(UNIT.prefixed[3], _(u'1 semaine'))
        self.assertEqual(UNIT['WEEK'], 3)
        self.assertEqual(UNIT.reverted[3], 'WEEK')

    def test_access_after_deepcopy(self):
        UNIT_ = deepcopy(UNIT)
        self.assertEqual(UNIT_.WEEK, 3)
        self.assertEqual(UNIT_[3], (3, _(u'semaine')))
        self.assertEqual(UNIT_.prefixed[3], _(u'1 semaine'))
        self.assertEqual(UNIT_['WEEK'], 3)
        self.assertEqual(UNIT_.reverted[3], 'WEEK')

    def test_day_amount(self):
        self.assertEqual(UNIT.units[0](24), 24)
        self.assertEqual(UNIT.units[1](30), 30)
        self.assertEqual(UNIT.units[2]( 3), 3)
        self.assertEqual(UNIT.units[3](28), 4)
        self.assertEqual(UNIT.units[4](28), 2)
        self.assertEqual(UNIT.units[5](30), 1)
        self.assertEqual(UNIT.units[6](30), 10)
        self.assertEqual(UNIT.units[7](30), 2)

    def test_day_amount_compat(self):
        self.assertEqual(UNIT.units[0](24), UNITS[0](24))
        self.assertEqual(UNIT.units[1](30), UNITS[1](30))
        self.assertEqual(UNIT.units[2]( 3), UNITS[2](3))
        self.assertEqual(UNIT.units[3](28), UNITS[3](28))
        self.assertEqual(UNIT.units[4](28), UNITS[4](28))
        self.assertEqual(UNIT.units[5](30), UNITS[5](30))
        self.assertEqual(UNIT.units[6](30), UNITS[6](30))
        self.assertEqual(UNIT.units[7](30), UNITS[7](30))

    def test_package(self):
        self.assertEqual(UNIT.package[0](UNIT.units[0](D('1')), timedelta(seconds=240)).quantize(D('.00')), D('0.07'))
        self.assertEqual(UNIT.package[1](UNIT.units[1](D('24')), timedelta(days=2)).quantize(D('.00')), D('48'))
        self.assertEqual(UNIT.package[2](UNIT.units[2](D('36')), timedelta(days=3)).quantize(D('.00')), D('36'))
        self.assertEqual(UNIT.package[3](UNIT.units[3](D('90')), timedelta(days=7)).quantize(D('.00')), D('90'))
        self.assertEqual(UNIT.package[4](UNIT.units[4](D('135')), timedelta(days=14)).quantize(D('.00')), D('135'))
        self.assertEqual(UNIT.package[5](UNIT.units[5](D('200')), timedelta(days=45)).quantize(D('.00')), D('300'))
        self.assertEqual(UNIT.package[6](UNIT.units[6](D('48')), timedelta(days=4)).quantize(D('.00')), D('64'))
        self.assertEqual(UNIT.package[7](UNIT.units[7](D('140')), timedelta(days=15)).quantize(D('.00')), D('140'))

    def test_package_comapt(self):
        self.assertEqual(UNIT.package[0](D('1'), timedelta(seconds=240)), PACKAGES[0](D('1'), timedelta(seconds=240)))
        self.assertEqual(UNIT.package[1](D('24'), timedelta(days=2)), PACKAGES[1](D('24'), timedelta(days=2)))
        self.assertEqual(UNIT.package[2](D('36'), timedelta(days=3)), PACKAGES[2](D('36'), timedelta(days=3)))
        self.assertEqual(UNIT.package[3](D('90'), timedelta(days=7)), PACKAGES[3](D('90'), timedelta(days=7)))
        self.assertEqual(UNIT.package[4](D('135'), timedelta(days=14)), PACKAGES[4](D('135'), timedelta(days=14)))
        self.assertEqual(UNIT.package[5](D('200'), timedelta(days=45)), PACKAGES[5](D('200'), timedelta(days=45)))
        self.assertEqual(UNIT.package[6](D('48'), timedelta(days=4)), PACKAGES[6](D('48'), timedelta(days=4)))
        self.assertEqual(UNIT.package[7](D('140'), timedelta(days=15)), PACKAGES[7](D('140'), timedelta(days=15)))

#------------------------------------------------------------------------------
# pylint: disable=too-many-public-methods
class KnowledgeBase(LazyObject):
    def _setup(self):
        _engine = knowledge_engine.engine((__file__, '.rules'))
        # add UNIT items as immutable facts (not affected by reset())
        for unit_name, unit_idx in UNIT.items():
            _engine.add_universal_fact('units', 'unit', (unit_name.lower(), unit_idx))
        self._wrapped = _engine

    def add_prices(self, *prices):
        for day_amount, unit in prices:
            self.assert_('prices', 'price', (unit, day_amount))

    def prove_price_unit(self, started_at, ended_at, kb_name='pricing'):
        delta = ended_at - started_at
        vals = self.prove_1_goal(
            '{}.pricing($unit, $started_at, $ended_at, $delta)'.format(kb_name),
            started_at=started_at, ended_at=ended_at, delta=delta
        )[0]
        return vals['unit']

kb = KnowledgeBase() # pylint: disable=invalid-name

try:
    from products.models import prove_price_unit
except ImportError:
    def prove_price_unit(prices, started_at, ended_at):
        delta = ended_at - started_at
        delta_days = delta.days
        if delta_days < 4 and delta_days >= 2 and \
            weekday(started_at.year, started_at.month, started_at.day) >= 4 and \
            weekday(ended_at.year, ended_at.month, ended_at.day) in (0, 6) and \
            UNIT.WEEK_END in prices:
            price_package = UNIT.WEEK_END
        elif delta_days >= monthrange(started_at.year, started_at.month)[1] and UNIT.MONTH in prices:
            price_package = UNIT.MONTH
        elif delta_days >= 15 and UNIT.FIFTEEN_DAYS in prices:
            price_package = UNIT.FIFTEEN_DAYS
        elif delta_days >= 14 and UNIT.TWO_WEEKS in prices:
            price_package = UNIT.TWO_WEEKS
        elif delta_days >= 7 and UNIT.WEEK in prices:
            price_package = UNIT.WEEK
        elif delta_days >= 3 and UNIT.THREE_DAYS in prices:
            price_package = UNIT.THREE_DAYS
        elif delta_days < 1 and delta.seconds > 0 and UNIT.HOUR in prices:
            price_package = UNIT.HOUR
        elif UNIT.DAY in prices:
            price_package = UNIT.DAY
        else:
            raise Exception('No price package could be proved')
        return price_package

#------------------------------------------------------------------------------
class BookingPricePackagesTestMixin(object):
    def test_week_end(self):
        started_at = datetime(2010, 9, 17, 9, 0)

        # note we do not have week-end price yet
        ended_at = started_at + timedelta(days=3)
        unit = self.prove_price(started_at, ended_at)
        self.assertEquals(unit, UNIT.DAY)

        # add week-end price and re-check
        self.add_prices((36, UNIT.WEEK_END))
        unit = self.prove_price(started_at, ended_at)
        self.assertEquals(unit, UNIT.WEEK_END)

        unit = self.prove_price(started_at, started_at + timedelta(days=1))
        self.assertEquals(unit, UNIT.DAY)

    def test_three_days(self):
        started_at = datetime(2010, 9, 17, 9, 0)

        # note we do not have week-end price yet
        ended_at = started_at + timedelta(days=3)
        unit = self.prove_price(started_at, ended_at)
        self.assertEquals(unit, UNIT.DAY)

        # add three-days price and re-check
        self.add_prices((48, UNIT.THREE_DAYS))
        unit = self.prove_price(started_at, ended_at)
        self.assertEquals(unit, UNIT.THREE_DAYS)

        unit = self.prove_price(started_at, started_at + timedelta(days=2))
        self.assertEquals(unit, UNIT.DAY)

        self.test_hour()

    def test_fifteen_days_and_two_weeks(self):
        started_at = datetime(2010, 9, 17, 9, 0)

        unit = self.prove_price(started_at, started_at + timedelta(days=15))
        self.assertEquals(unit, UNIT.DAY)
        unit = self.prove_price(started_at, started_at + timedelta(days=14))
        self.assertEquals(unit, UNIT.DAY)

        self.add_prices((360, UNIT.TWO_WEEKS), (360, UNIT.FIFTEEN_DAYS))

        unit = self.prove_price(started_at, started_at + timedelta(days=21))
        self.assertEquals(unit, UNIT.FIFTEEN_DAYS)
        unit = self.prove_price(started_at, started_at + timedelta(days=15))
        self.assertEquals(unit, UNIT.FIFTEEN_DAYS)
        unit = self.prove_price(started_at, started_at + timedelta(days=14))
        self.assertEquals(unit, UNIT.TWO_WEEKS)

        unit = self.prove_price(started_at, started_at + timedelta(days=13))
        self.assertEquals(unit, UNIT.DAY)

        self.test_week()

    def test_week(self):
        started_at = datetime(2010, 9, 17, 9, 0)

        # note we do not have hour price yet
        ended_at = started_at + timedelta(days=10)
        unit = self.prove_price(started_at, ended_at)
        self.assertEquals(unit, UNIT.DAY)

        self.add_prices((128, UNIT.WEEK))
        unit = self.prove_price(started_at, ended_at)
        self.assertEquals(unit, UNIT.WEEK)

        unit = self.prove_price(started_at, started_at + timedelta(days=5))
        self.assertEquals(unit, UNIT.DAY)

        self.test_three_days()

    def test_hour(self):
        started_at = datetime(2010, 9, 17, 9, 0)

        # note we do not have hour price yet
        ended_at = started_at + timedelta(seconds=60*60*3)
        unit = self.prove_price(started_at, ended_at)
        self.assertEquals(unit, UNIT.DAY)

        self.add_prices((1, UNIT.HOUR))
        unit = self.prove_price(started_at, ended_at)
        self.assertEquals(unit, UNIT.HOUR)

    def test_month(self):
        started_at = datetime(2010, 9, 17, 9, 0)

        # note we do not have month price yet
        ended_at = started_at + timedelta(days=45)
        unit = self.prove_price(started_at, ended_at)
        self.assertEquals(unit, UNIT.DAY)

        self.add_prices((480, UNIT.MONTH))
        unit = self.prove_price(started_at, ended_at)
        self.assertEquals(unit, UNIT.MONTH)

        unit = self.prove_price(started_at, started_at + timedelta(days=29))
        self.assertEquals(unit, UNIT.DAY)

        # check 2-weeks and 15-days when we have month price
        self.test_fifteen_days_and_two_weeks()

class BookingPricePackagesMixin(object):
    kb_name = 'pricing_new'

    def tearDown(self): # pylint: disable=invalid-name,no-self-use
        kb.reset()

    def prove_price(self, started_at, ended_at):
        return kb.prove_price_unit(started_at, ended_at, kb_name=self.kb_name)

    def add_prices(self, *prices): # pylint: disable=no-self-use
        kb.add_prices(*prices)

class BookingPricePackagesTest(BookingPricePackagesMixin, BookingPricePackagesTestMixin, unittest.TestCase):
    def setUp(self): # pylint: disable=invalid-name
        self.add_prices((24, UNIT.DAY))
        kb.activate(self.kb_name)

class BookingPricePackagesOrigTest(BookingPricePackagesTest):
    kb_name = 'pricing_orig'

    def prove_price(self, started_at, ended_at):
        package_name = super(BookingPricePackagesOrigTest, self).prove_price(started_at, ended_at)
        return PACKAGES_UNIT[package_name]

class BookingPricePackagesPythonMixin(object):
    prices = set()

    def tearDown(self): # pylint: disable=invalid-name
        self.prices.clear()

    def prove_price(self, started_at, ended_at):
        return prove_price_unit(self.prices, started_at, ended_at)

    def add_prices(self, *prices):
        self.prices.update(set((unit for day_amount, unit in prices)))

class BookingPricePackagesPythonTest(BookingPricePackagesPythonMixin, BookingPricePackagesTestMixin, unittest.TestCase): # pylint: disable=too-many-public-methods
    def setUp(self): # pylint: disable=invalid-name
        self.add_prices((24, UNIT.DAY))

# -----------------------------------------------------------------------------
from itertools import cycle
try:
    # try to get number of runs by means of nose-testconfig
    from testconfig import config
    RUNS = int(config.get('runs', 1))
except ImportError:
    RUNS = 1

class PerformanceTestMixin(object):
    def setUp(self): # pylint: disable=invalid-name
        self.add_prices(
            (1, UNIT.HOUR),
            (24, UNIT.DAY),
            (36, UNIT.WEEK_END),
            (48, UNIT.THREE_DAYS),
            (148, UNIT.WEEK),
            (360, UNIT.TWO_WEEKS),
            (360, UNIT.FIFTEEN_DAYS),
            (480, UNIT.MONTH),
        )

    def run_n_times(self, **kwargs):
        started_at = datetime(2010, 9, 17, 9, 0)
        days = cycle([2, 5, 3, 18, 34, 13, 6])
        for i in xrange(RUNS): # pylint: disable=unused-variable
            ended_at = started_at + timedelta(days=days.next())
            self.prove_price(started_at, ended_at)
        self.assertTrue(True)

class PerformanceTest(BookingPricePackagesMixin, PerformanceTestMixin, unittest.TestCase):
    def test_pricing(self):
        self.kb_name = 'pricing_new'
        kb.activate(self.kb_name)
        self.run_n_times()

    def test_pricing_orig(self):
        self.kb_name = 'pricing_orig'
        kb.activate(self.kb_name)
        self.run_n_times()

class PerformanceOrigTest(PerformanceTestMixin, unittest.TestCase):
    kb_name = 'pricing'
    prices = ()
    __FILE__ = os.path.abspath(os.path.join(__file__, '..', '..', 'models.py'))

    def tearDown(self): # pylint: disable=invalid-name
        self.prices = ()

    def prove_price(self, started_at, ended_at):
        engine = knowledge_engine.engine((PerformanceOrigTest.__FILE__, '.rules'))
        engine.activate(self.kb_name)

        for day_amount, unit in self.prices:
            engine.assert_('prices', 'price', (unit, day_amount))

        delta = ended_at - started_at
        vals, plans = engine.prove_1_goal( # pylint: disable=unused-variable
            '{}.pricing($type, $started_at, $ended_at, $delta)'.format(self.kb_name),
            started_at=started_at, ended_at=ended_at, delta=delta
        )
        unit = PACKAGES_UNIT[vals['type']] # pylint: disable=unused-variable

        engine.reset()

    def add_prices(self, *prices):
        self.prices += prices

    def test_pricing_orig(self):
        self.run_n_times()

class PerformancePythonTest(BookingPricePackagesPythonMixin, PerformanceTestMixin, unittest.TestCase):
    def test_pricing_python(self):
        self.run_n_times()

if __name__ == '__main__':
    unittest.main()
