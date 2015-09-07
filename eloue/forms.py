from django import forms

class ContactFormPro(forms.Form):
    name = forms.CharField(max_length=100, initial="")
    sender = forms.EmailField(max_length=50, initial="")
    phone_number = forms.CharField(max_length= 12, required=False, initial="")
    activity_field = forms.CharField(max_length=100, initial="")