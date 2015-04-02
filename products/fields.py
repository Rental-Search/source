# -*- coding: utf-8 -*-
import datetime

from django.db import models
from django.core import exceptions
from django import forms

class SimpleDate(int):
    def __new__(cls, value):
        return int.__new__(cls, cls.format(value))
    
    @classmethod
    def format(cls, value):
        """
        >>> SimpleDate.format(283)
        283
        >>> SimpleDate.format(datetime.date(2010, 8, 27))
        283
        >>> SimpleDate.format(datetime.datetime(2010, 8, 27))
        283
        >>> SimpleDate.format('283')
        283
        """
        if isinstance(value, int):
            return value
        if isinstance(value, datetime.datetime):
            return int((32 * value.month) + value.day)
        if isinstance(value, datetime.date):
            return int((32 * value.month) + value.day)
        return int(value)
    
    def date(self, year):
        """Returns corresponding date object
        >>> SimpleDate(283).date(2010)
        datetime.date(2010, 8, 27)
        """
        return datetime.date(year, self.month, self.day)
    
    def datetime(self, year):
        """Returns corresponding datetime object
        >>> SimpleDate(283).datetime(2010)
        datetime.datetime(2010, 8, 27, 0, 0)
        """
        return datetime.datetime(year, self.month, self.day)
    
    @property
    def day(self):
        """
        >>> date = SimpleDate(33)
        >>> date.day
        1
        >>> date = SimpleDate(415)
        >>> date.day
        31
        """
        return self - (32 * self.month)
    
    @property
    def month(self):
        """
        >>> date = SimpleDate(415)
        >>> date.month
        12
        >>> date = SimpleDate(33)
        >>> date.month
        1
        """
        return self / 32
    

class SimpleDateField(models.PositiveSmallIntegerField):
    __metaclass__ = models.SubfieldBase
    
    def to_python(self, value):
        """
        >>> from django.utils.translation import activate
        >>> activate('en-gb')
        >>> SimpleDateField().to_python(283)
        283
        >>> SimpleDateField().to_python(None)
        >>> SimpleDateField().to_python(2.3)
        2
        >>> SimpleDateField().to_python("2.3")
        Traceback (most recent call last):
        ...
        ValidationError: [u"'%s' value must be an integer."]
        """
        if value is None:
            return None
        try:
            return SimpleDate(value)
        except (TypeError, ValueError):
            raise exceptions.ValidationError(self.error_messages['invalid'])
    
    def get_prep_value(self, value):
        """
        >>> SimpleDateField().get_prep_value(None)
        >>> SimpleDateField().get_prep_value(283)
        283
        >>> SimpleDateField().get_prep_value(datetime.date(2010, 8, 27))
        283
        >>> SimpleDateField().get_prep_value(datetime.datetime(2010, 8, 27))
        283
        >>> SimpleDateField().get_prep_value('283')
        283
        """
        if value is None:
            return None
        if isinstance(value, datetime.datetime):
            return int((32 * value.month) + value.day)
        if isinstance(value, datetime.date):
            return int((32 * value.month) + value.day)
        return int(value)
    
    def south_field_triple(self):
        from south.modelsinspector import introspector
        field_class = "django.db.models.fields.PositiveSmallIntegerField"
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)


class FacetField(forms.CharField):
    def __init__(self, pretty_name=None, *args, **kwargs):
        self.pretty_name = pretty_name
        super(FacetField, self).__init__(*args, **kwargs)
