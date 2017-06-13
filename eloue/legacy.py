from django.forms import HiddenInput
from django.http import Http404
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.utils.crypto import constant_time_compare
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.formtools.utils import form_hmac
from django.contrib.sites.models import get_current_site
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django import forms


class GenerateOptimistic(object):
    """
    A strategy that acts immediately when the source file changes and assumes
    that the cache files will not be removed (i.e. it doesn't ensure the
    cache file exists when it's accessed).
    """
    def on_source_saved(self, file_obj):
        try:
            file_obj.generate()
        except:
            pass

    def should_verify_existence(self, file_obj):
        return False

class GenerateOnUpload(object):
    def on_source_saved(self, file_obj):
        try:
            file_obj.generate()
        except:
            pass

class GenerateOnDownload(object):
    def on_content_required(self, file_obj):
        try:
            file_obj.generate()
        except:
            pass

class GenerateOnContent(GenerateOnDownload, GenerateOnUpload):
    pass

class GenerateOnAnyAccess(GenerateOnContent):
    def on_existence_required(self, file_obj):
        try:
            file_obj.generate()
        except IOError:
            pass


def new_message_email(sender, instance, signal,
        subject_prefix=_(u'New Message: %(subject)s'),
        template_name="django_messages/new_message",
        default_protocol=None,
        *args, **kwargs):
    """
    This function sends an email and is called via Django's signal framework.
    Optional arguments:
        ``template_name``: the template to use
        ``subject_prefix``: prefix for the email subject.
        ``default_protocol``: default protocol in site URL passed to template
    """
    if default_protocol is None:
        default_protocol = getattr(settings, 'DEFAULT_HTTP_PROTOCOL', 'http')

    if 'created' in kwargs and kwargs['created']:
        try:
            current_domain = get_current_site().domain
            subject = subject_prefix % {'subject': instance.subject}
            context = {
                'site_url': '%s://%s' % (default_protocol, current_domain),
                'message': instance,
            }
            text_content = render_to_string("%s.txt" % template_name, context)
            html_content = render_to_string("%s.html" % template_name, context)
            if instance.recipient.email != "":
                message = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [instance.recipient.email,])
                message.attach_alternative(html_content, "text/html")
                message.send()

        except Exception as e:
            #print e
            pass #fail silently


# TODO: remove backported forms.fields.TypedChoiceField from Django 1.7b4 after upgrade to Django 1.7 release
class TypedChoiceField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        self.coerce = kwargs.pop('coerce', lambda val: val)
        self.empty_value = kwargs.pop('empty_value', '')
        super(TypedChoiceField, self).__init__(*args, **kwargs)

    def _coerce(self, value):
        """
        Validate that the value can be coerced to the right type (if not empty).
        """
        if value == self.empty_value or value in self.empty_values:
            return self.empty_value
        try:
            value = self.coerce(value)
        except (ValueError, TypeError, ValidationError):
            raise ValidationError(
                self.error_messages['invalid_choice'],
                code='invalid_choice',
                params={'value': value},
            )
        return value

    def clean(self, value):
        value = super(TypedChoiceField, self).clean(value)
        return self._coerce(value)
