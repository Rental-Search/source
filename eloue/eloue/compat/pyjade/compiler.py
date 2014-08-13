
import re

from django import template

from pyjade.ext.django.compiler import Compiler as _Compiler

class Compiler(_Compiler):
    RE_INTERPOLATE = re.compile(r'(\\)?([#!]){([^\[]*)(?:\s*\[\s*(\d+)\s*\])?}')

    def visitExtends(self,node):
        path = self.format_path(node.path)
        self.buffer('{%% extends "%(path)s" %%}{%% __pyjade_loadkwacros "%(path)s" %%}' % {'path': path})

    def visitInclude(self,node):
        path = self.format_path(node.path)
        self.buffer('{%% include "%(path)s" %%}{%% __pyjade_loadkwacros "%(path)s" %%}' % {'path': path})

    def interpolate(self, text, escape=True):
        return self.RE_INTERPOLATE.sub(
            lambda m: ''.join([
                self.variable_start_string,
                m.group(3),
                '.' + m.group(4) if m.group(4) else '',
                '|escape' if escape else '',
                self.variable_end_string,
            ]),
            text
        )

template.add_to_builtins('eloue.compat.pyjade.templatetags')
