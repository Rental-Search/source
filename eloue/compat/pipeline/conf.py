# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings as _settings

from pipeline.conf import DEFAULTS

DEFAULTS.update({
    'PIPELINE_AUTOPREFIXER_BINARY': '/usr/local/bin/autoprefixer',
    'PIPELINE_AUTOPREFIXER_ARGUMENTS': '',
})

class PipelineSettings(object):
    '''
    Lazy Django settings wrapper for Django Pipeline
    '''
    def __init__(self, wrapped_settings):
        self.wrapped_settings = wrapped_settings

    def __getattr__(self, name):
        if hasattr(self.wrapped_settings, name):
            return getattr(self.wrapped_settings, name)
        elif name in DEFAULTS:
            return DEFAULTS[name]
        else:
            raise AttributeError("'%s' setting not found" % name)

settings = PipelineSettings(_settings)
