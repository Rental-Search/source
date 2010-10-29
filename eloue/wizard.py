# -*- coding: utf-8 -*-
try:
    import cPickle as pickle
except ImportError:
    import pickle

import django.forms as forms
from django.conf import settings
from django.contrib.auth import login
from django.contrib.formtools.wizard import FormWizard
from django.http import Http404
from django.utils.decorators import method_decorator
from django.utils.hashcompat import md5_constructor
from django.views.decorators.csrf import csrf_protect

from eloue.accounts.forms import EmailAuthenticationForm, make_missing_data_form
from eloue.accounts.models import Patron


class CustomFormWizard(FormWizard):
    def get_form(self, step, data=None, files=None):
        return self.form_list[step](data, files, prefix=self.prefix_for_step(step), initial=self.initial.get(step, None))
    
    def security_hash(self, request, form):
        data = []
        for bf in form:
            # Get the value from the form data. If the form allows empty or hasn't
            # changed then don't call clean() to avoid trigger validation errors
            if isinstance(bf.field, forms.FileField):
                continue
            if form.empty_permitted and not form.has_changed():
                value = bf.data or ''
            else:
                value = bf.field.clean(bf.data) or ''
            if isinstance(value, basestring):
                value = value.strip()
            data.append((bf.name, value))
        data.append(settings.SECRET_KEY)
        
        pickled = pickle.dumps(data, pickle.HIGHEST_PROTOCOL)
        return md5_constructor(pickled).hexdigest()
    
    def render(self, form, request, step, context=None):
        old_data, old_files = request.POST, request.FILES
        prev_fields = []
        if old_data:
            hidden = forms.HiddenInput()
            # Collect all data from previous steps and render it as HTML hidden fields.
            for i in range(step):
                old_form = self.get_form(i, old_data, old_files)
                hash_name = 'hash_%s' % i
                prev_fields.extend([bf.as_hidden() for bf in old_form])
                prev_fields.append(hidden.render(hash_name, old_data.get(hash_name, self.security_hash(request, old_form))))
        return self.render_template(request, form, ''.join(prev_fields), step, context)
    
    @method_decorator(csrf_protect)
    def __call__(self, request, *args, **kwargs):
        if 'extra_context' in kwargs:
            self.extra_context.update(kwargs['extra_context'])
        current_step = self.determine_step(request, *args, **kwargs)
        self.parse_params(request, *args, **kwargs)
        
        # Sanity check.
        if current_step >= self.num_steps():
            raise Http404('Step %s does not exist' % current_step)
        
        # For each previous step, verify the hash and process.
        # TODO: Move "hash_%d" to a method to make it configurable.
        for i in range(current_step):
            form = self.get_form(i, request.POST, request.FILES)
            if request.POST.get("hash_%d" % i, '') != self.security_hash(request, form):
                return self.render_hash_failure(request, i)
            self.process_step(request, form, i)
        
        # Process the current step. If it's valid, go to the next step or call
        # done(), depending on whether any steps remain.
        if request.method == 'POST':
            form = self.get_form(current_step, request.POST, request.FILES)
        else:
            form = self.get_form(current_step)
        if form.is_valid():
            self.process_step(request, form, current_step)
            next_step = current_step + 1
            
            # If this was the last step, validate all of the forms one more
            # time, as a sanity check, and call done().
            num = self.num_steps()
            if next_step == num:
                final_form_list = [self.get_form(i, request.POST, request.FILES) for i in range(num)]
                
                # Validate all the forms. If any of them fail validation, that
                # must mean the validator relied on some other input, such as
                # an external Web site.
                for i, f in enumerate(final_form_list):
                    if not f.is_valid():
                        return self.render_revalidation_failure(request, i, f)
                return self.done(request, final_form_list)
            
            # Otherwise, move along to the next step.
            else:
                form = self.get_form(next_step)
                self.step = current_step = next_step
        
        return self.render(form, request, current_step)
    

class GenericFormWizard(CustomFormWizard):
    def done(self, request, form_list):
        missing_form = form_list[-1]
        
        if request.user.is_anonymous(): # Create new Patron
            auth_form = form_list[1]
            new_patron = auth_form.get_user()
            if not new_patron:
                new_patron = Patron.objects.create_inactive(missing_form.cleaned_data['username'],
                    auth_form.cleaned_data['email'], missing_form.cleaned_data['password1'])
            if not hasattr(new_patron, 'backend'):
                from django.contrib.auth import load_backend
                backend = load_backend(settings.AUTHENTICATION_BACKENDS[0])
                new_patron.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
            login(request, new_patron)
        else:
            new_patron = request.user
        
        missing_form.instance = new_patron
        new_patron, new_address, new_phone = missing_form.save()
        return new_patron, new_address, new_phone
    
    def __call__(self, request, *args, **kwargs):
        if request.user.is_authenticated(): # When user is authenticated
            if EmailAuthenticationForm in self.form_list:
                self.form_list.remove(EmailAuthenticationForm)
            if not any(map(lambda el: getattr(el, '__name__', None) == 'MissingInformationForm', self.form_list)):
                self.form_list.append(make_missing_data_form(request.user))
        else: # When user is anonymous
            if EmailAuthenticationForm not in self.form_list:
                self.form_list.append(EmailAuthenticationForm)
            if EmailAuthenticationForm in self.form_list:
                if not any(map(lambda el: getattr(el, '__name__', None) == 'MissingInformationForm', self.form_list)):
                    form = self.get_form(self.form_list.index(EmailAuthenticationForm), request.POST, request.FILES)
                    form.is_valid() # Here to fill form user_cache
                    self.form_list.append(make_missing_data_form(form.get_user()))
        return super(GenericFormWizard, self).__call__(request, *args, **kwargs)
    
