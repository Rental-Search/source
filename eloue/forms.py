from django import forms

class ContactFormPro(forms.Form):
    name = forms.CharField(max_length=100)
    sender = forms.EmailField(max_length=50)
    phone_number = forms.CharField(max_length= 12, required=False)
    activity_field = forms.CharField(max_length=100)