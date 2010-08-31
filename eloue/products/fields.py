# -*- coding: utf-8 -*-
import datetime
from django.db import models
from django.core import exceptions
import django.forms as forms

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
    

class SimpleDateField(models.IntegerField):
    __metaclass__ = models.SubfieldBase
    
    def to_python(self, value):
        """
        >>> SimpleDateField().to_python(283)
        283
        >>> SimpleDateField().to_python(None)
        >>> SimpleDateField().to_python(2.3)
        2
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
    

class FacetField(forms.CharField):
    def __init__(self, pretty_name=None, *args, **kwargs):
        self.pretty_name = pretty_name
        super(FacetField, self).__init__(*args, **kwargs)
    
