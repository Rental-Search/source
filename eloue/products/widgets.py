#!/usr/bin/python
# -*- coding: utf-8 -*-
import django.forms as forms
from django.utils.safestring import mark_safe
from django.utils.encoding import smart_unicode

class PriceTextInput(forms.TextInput):
    def render(self, name, value, attrs=None):
        import locale
        from django.conf import settings
        from decimal import Decimal as D
        from django.utils import translation
        old_locale = locale.getlocale()
        if settings.CONVERT_XPF:
            return mark_safe(super(PriceTextInput, self).render(name, value, attrs) + ' <span class="unit"> XPF</span>')
        try:
            new_locale = locale.normalize(translation.to_locale("%s.utf8" % translation.get_language()))
            locale.setlocale(locale.LC_ALL, new_locale)
            return mark_safe(super(PriceTextInput, self).render(name, value, attrs) + u' <span class="unit">'+smart_unicode(locale.localeconv()['currency_symbol'])+u'</span>')
        except (TypeError, locale.Error):
            return mark_safe(super(PriceTextInput, self).render(name, value, attrs) + ' <span class="unit"></span>')
        finally:
            locale.setlocale(locale.LC_ALL, old_locale)




class CommentedSelectInput(forms.Select):
    def __init__(self, info_text, attrs={'class': 'price'}):
        super(CommentedSelectInput, self).__init__(attrs)
        from django.utils.html import escape
        self.info_text = escape(info_text)

    def render(self, name, value, attrs=None):
        from django.utils.safestring import mark_safe
        return mark_safe(super(CommentedSelectInput, self).render(name, value, attrs) + '<span class="unit"> ' + self.info_text + '</span>')


class CommentedTextInput(forms.TextInput):
    def __init__(self, info_text, attrs={'class': 'price'}):
        super(CommentedTextInput, self).__init__(attrs)
        from django.utils.html import escape
        self.info_text = escape(info_text)

    def render(self, name, value, attrs=None):
        from django.utils.safestring import mark_safe
        return mark_safe(super(CommentedTextInput, self).render(name, value, attrs) + '<span class="unit"> ' + self.info_text + '</span>')