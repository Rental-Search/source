import datetime
from django import forms
from eloue.products.utils import Enum

INTERVAL_CHOICES = Enum([
    ('days', 'days', u'days'),
    ('months', 'months', u'months'),
    ('weeks', 'weeks', u'weeks'),
])

class TimeSeriesForm(forms.Form):
	start_date = forms.DateField(required=True)
	end_date = forms.DateField(required=True)
	interval = forms.ChoiceField(choices=INTERVAL_CHOICES, required=True)

	def clean(self):
		cleaned_data = super(TimeSeriesForm, self).clean()
		start_date = cleaned_data.get('start_date')
		end_date = cleaned_data.get('end_date')

		if start_date and end_date and start_date > end_date:
			msg = "start_date must be lower than end_date"
			raise forms.ValidationError(msg)

		return cleaned_data