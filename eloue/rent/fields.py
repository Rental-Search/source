# -*- coding: utf-8 -*-
import uuid

from django.db import models


class IntegerAutoField(models.IntegerField):
    empty_strings_allowed = False
    
    def __init__(self, *args, **kwargs):
        kwargs['blank'] = True
        super(IntegerAutoField, self).__init__(*args, **kwargs)

    def validate(self, value, model_instance):
        pass
    
    def db_type(self, connection):
        return 'serial'
    
    def formfield(self, **kwargs):
        return None
    
    def south_field_triple(self):
        from south.modelsinspector import introspector
        field_class = "django.db.models.fields.IntegerField"
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)
    

class UUIDVersionError(Exception):
    pass


class UUIDField(models.CharField):
    """
    A field which stores a UUID value in hex format. This may also have
    the Boolean attribute 'auto' which will set the value on initial save to a
    new UUID value (calculated using the UUID1 method). Note that while all
    UUIDs are expected to be unique we enforce this with a DB constraint.
    """
    __metaclass__ = models.SubfieldBase
 
    def __init__(self, version=4, node=None, clock_seq=None, namespace=None, auto=True, name=None, *args, **kwargs):
        if version not in (1, 3, 4, 5):
            raise UUIDVersionError("UUID version %s is not supported." % version)
        self.auto = auto
        self.version = version
        kwargs['max_length'] = 32  # Set this as a fixed value, we store UUIDs in text.
        if auto:  # Do not let the user edit UUIDs if they are auto-assigned.
            kwargs['editable'] = False
            kwargs['blank'] = True
            kwargs['unique'] = True
        if version == 1:
            self.node, self.clock_seq = node, clock_seq
        elif version in (3, 5):
            self.namespace, self.name = namespace, name
        super(UUIDField, self).__init__(*args, **kwargs)
    
    def _create_uuid(self):
        if not self.version or self.version == 4:
            return uuid.uuid4()
        elif self.version == 1:
            return uuid.uuid1(self.node, self.clock_seq)
        elif self.version == 2:
            raise UUIDVersionError("UUID version 2 is not supported.")
        elif self.version == 3:
            return uuid.uuid3(self.namespace, self.name)
        elif self.version == 5:
            return uuid.uuid5(self.namespace, self.name)
        else:
            raise UUIDVersionError("UUID version %s is not valid." % self.version)
    
    def pre_save(self, model_instance, add):
        if self.auto and add:
            value = self._create_uuid()
            setattr(model_instance, self.attname, value)
            return value
        else:
            value = super(UUIDField, self).pre_save(model_instance, add)
            if self.auto and not value:
                value = self._create_uuid()
                setattr(model_instance, self.attname, value)
        return value
    
    def to_python(self, value):
        if not value:
            return
        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(value)
        return value
    
    def get_prep_value(self, value):
        if not value:
            return
        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(value)
        return value.hex
    
    def south_field_triple(self):
        from south.modelsinspector import introspector
        field_class = "django.db.models.fields.CharField"
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)
    

