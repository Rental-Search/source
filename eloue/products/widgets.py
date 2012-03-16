import django.forms as forms
from django.utils.safestring import mark_safe

class PriceTextInput(forms.TextInput):
    
    def render(self, name, value, attrs=None):
        return mark_safe(super(PriceTextInput, self).render(name, value, attrs) + ' <span class="unit"> &euro;</span>')


class CommentedSelectInput(forms.Select):

    def __init__(self, info_text, attrs={'class': 'price'}):
        super(CommentedSelectInput, self).__init__(attrs)
        from django.utils.html import escape
        self.info_text = escape(info_text)

    def render(self, name, value, attrs=None):
        from django.utils.safestring import mark_safe
        return mark_safe(super(CommentedSelectInput, self).render(name, value, attrs) + '<span class="unit"> ' + self.info_text + '</span>')