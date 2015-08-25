from django import forms
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect

class ContactForm(forms.Form):
	email = forms.CharField(label='Your name', max_length=100, type = email)
	category = forms.list(label='category', max_length=50)
	objet = forms.CharField(label='objet', max_length=500)
	message = forms.CharField(widget=forms.Textarea)
	# I can also send email using the self.cleaned_data dictionary

	def is_valid(*args):
		is_valid = False
		#if ....
		return True

	def send_email(request):
	    objet = request.POST.get('objet', '')
	    message = request.POST.get('message', '')
	    from_email = request.POST.get('email', '')

	    if is_valid:
	        try:
	            send_mail(subject, message, from_email, ['admin@example.com'])
	        except BadHeaderError:
	            return HttpResponse('Invalid header found.')
	        return HttpResponseRedirect('/contact/thanks/')
	    else:
	        # In reality we'd use a form class
	        # to get proper validation errors.
	        return HttpResponse('Make sure all fields are entered and valid.')