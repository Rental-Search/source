# -*- coding: utf-8 -*-
from django.forms.widgets import RadioFieldRenderer, RadioInput, CheckboxInput
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe


class ParagraphRadioFieldRenderer(RadioFieldRenderer):
    def __iter__(self):
        for i, choice in enumerate(self.choices):
            yield RadioInput(self.name, self.value, self.attrs.copy(), choice, i)
    
    def __getitem__(self, idx):
        choice = self.choices[idx]  # Let the IndexError propogate
        return RadioInput(self.name, self.value, self.attrs.copy(), choice, idx)
    
    def render(self):
        return mark_safe(u'\n'.join([u'%s' % force_unicode(w) for w in self]))


class CommentedCheckboxInput(CheckboxInput):

    def __init__(self, info_text, attrs=None, check_test=bool):
        super(CommentedCheckboxInput, self).__init__(attrs, check_test)
        from django.utils.html import escape
        self.info_text = escape(info_text)

    def render(self, name, value, attrs=None):
        from django.utils.safestring import mark_safe
        return mark_safe('<label class="checkbox">' + super(CommentedCheckboxInput, self).render(name, value, attrs) + '\t' + self.info_text + '</label>')
    
