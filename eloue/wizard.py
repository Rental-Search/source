# -*- coding: utf-8 -*-
from django.contrib.formtools.wizard import FormWizard
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

class CustomFormWizard(FormWizard):
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
            form = self.get_form(i, request.POST)
            if request.POST.get("hash_%d" % i, '') != self.security_hash(request, form):
                return self.render_hash_failure(request, i)
            self.process_step(request, form, i)
        
        # Process the current step. If it's valid, go to the next step or call
        # done(), depending on whether any steps remain.
        if request.method == 'POST':
            form = self.get_form(current_step, request.POST)
        else:
            form = self.get_form(current_step)
        if form.is_valid():
            self.process_step(request, form, current_step)
            next_step = current_step + 1
            
            # If this was the last step, validate all of the forms one more
            # time, as a sanity check, and call done().
            num = self.num_steps()
            if next_step == num:
                final_form_list = [self.get_form(i, request.POST) for i in range(num)]
                
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
    
