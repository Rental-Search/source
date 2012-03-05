import django.forms as forms
from django.utils.safestring import mark_safe

class PriceTextInput(forms.TextInput):
    
    def render(self, name, value, attrs=None):
        return mark_safe(super(PriceTextInput, self).render(name, value, attrs) + ' <span class="unit"> &euro;</span>')