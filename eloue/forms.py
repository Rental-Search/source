from django import forms

class ContactForm(forms.Form):
	message = forms.CharField(widget=forms.Textarea, initial="")
	sender = forms.EmailField(label='Your name', max_length=100, initial="")
	category = forms.CharField(widget=forms.Select)
	cc_myself = forms.BooleanField(required=False)