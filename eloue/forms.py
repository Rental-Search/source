from django import forms

class ContactForm(forms.Form):
	email = forms.EmailField(label='Your name', max_length=100)
	category = forms.MultipleChoiceField(label='category')
	objet = forms.CharField(label='objet', max_length=500)
	message = forms.CharField(widget=forms.Textarea)