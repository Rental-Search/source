# -*- coding: utf-8 -*-
from django.forms.widgets import RadioFieldRenderer, RadioInput
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

class CustomRadioInput(RadioInput):
    def __unicode__(self):
        if 'id' in self.attrs:
            label_for = ' for="%s_%s"' % (self.attrs['id'], self.index)
        else:
            label_for = ''
        choice_label = conditional_escape(force_unicode(self.choice_label))
        return mark_safe(u'<td class="txtR txtT">%s</td><td><label class="labb"%s>%s</label></td>' % (self.tag(), label_for, choice_label))
    

class CustomRadioFieldRenderer(RadioFieldRenderer):
    def __iter__(self):
        for i, choice in enumerate(self.choices):
            yield CustomRadioInput(self.name, self.value, self.attrs.copy(), choice, i)
    
    def __getitem__(self, idx):
        choice = self.choices[idx] # Let the IndexError propogate
        return CustomRadioInput(self.name, self.value, self.attrs.copy(), choice, idx)
    
    def render(self):
        return mark_safe(u'\n'.join([u'<tr class="cSign">%s</tr>' % force_unicode(w) for w in self]))
    
