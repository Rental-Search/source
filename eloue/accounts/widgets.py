# -*- coding: utf-8 -*-
from django.forms.widgets import RadioFieldRenderer, RadioInput
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe


class ParagraphRadioFieldRenderer(RadioFieldRenderer):
    def __iter__(self):
        for i, choice in enumerate(self.choices):
            yield RadioInput(self.name, self.value, self.attrs.copy(), choice, i)
    
    def __getitem__(self, idx):
        choice = self.choices[idx] # Let the IndexError propogate
        return RadioInput(self.name, self.value, self.attrs.copy(), choice, idx)
    
    def render(self):
        return mark_safe(u'\n'.join([u'<p>%s</p>' % force_unicode(w) for w in self]))
    
