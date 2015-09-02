from django import forms

class ContactFormPro(forms.Form):
    name = forms.CharField(max_length=100)
    sender = forms.EmailField(max_length=100)
    phone_number = forms.CharField()
    activity_field = forms.CharField(max_length=100)