from django import forms

class ContactForm(forms.Form):
	message = forms.CharField(widget=forms.Textarea)
	sender = forms.EmailField(label='Your name', max_length=100)
	category = forms.CharField(label='objet', max_length=100)
	cc_myself = forms.BooleanField(required=False)