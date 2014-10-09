# -*- coding: utf-8 -*-
from django.http import HttpResponseNotFound, Http404
from django.views.decorators.csrf import requires_csrf_token
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import View, TemplateView
from django.template import RequestContext, loader
from django.utils.translation import ugettext_lazy as _

from haystack.query import SearchQuerySet
from haystack.constants import DJANGO_ID

from products.forms import FacetedSearchForm
from eloue.http import JsonResponse

@requires_csrf_token
def custom404(request, template_name='404.html'):
    """
    Default 404 handler.

    Templates: `404.html`
    Context:
        request_path
            The path of the requested URL (e.g., '/app/pages/bad_page/')
    """
    t = loader.get_template(template_name) # You need to create a 404.html template.
    form = FacetedSearchForm()
    return HttpResponseNotFound(
    	t.render(RequestContext(request, {'request_path': request.path, 'form': form}))
    )

class LoginRequiredMixin(View):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)

class SearchQuerySetMixin(object):
    def dispatch(self, request, *args, **kwargs):
        self.sqs = kwargs.pop('sqs', SearchQuerySet())
        self.load_all = kwargs.pop('load_all', False)
        return super(SearchQuerySetMixin, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        sqs = self.sqs
        return sqs.load_all() if self.load_all else sqs

    def get_object(self, queryset=None):
        """
        Returns the object the view is displaying.
        """
        # Use a custom queryset if provided; this is required for subclasses
        # like DateDetailView
        if queryset is None:
            queryset = self.get_queryset()

        # Next, try looking up by primary key.
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        slug = self.kwargs.get(self.slug_url_kwarg, None)
        if pk is not None:
            queryset = queryset.filter(**{DJANGO_ID: pk})

        # Next, try looking up by slug.
        elif slug is not None:
            slug_field = self.get_slug_field()
            queryset = queryset.filter(**{slug_field: slug})

        # If none of those are defined, it's an error.
        else:
            raise AttributeError("Generic detail view %s must be called with "
                                 "either an object pk or a slug."
                                 % self.__class__.__name__)

        try:
            # Get the single item from the filtered queryset
            obj = queryset.best_match()
        except IndexError:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': self.model._meta.verbose_name})
        return obj

class AjaxResponseMixin(object):
    response_class = JsonResponse

    def render_to_response(self, context, **kwargs):
        return self.response_class(context, **kwargs)

class BreadcrumbsMixin(object):
    breadcrumbs = {
        'sort': {'name': 'sort', 'value': None, 'label': 'sort', 'facet': False},
        'q': {'name': 'q', 'value': None, 'label': 'q', 'facet': False},
        'l': {'name': 'l', 'value': None, 'label': 'l', 'facet': False},
        'r': {'name': 'r', 'value': None, 'label': 'r', 'facet': False},
        'renter': {'name': 'renter', 'value': None, 'label': 'renter', 'facet': False},
    }

    def get_context_data(self, **kwargs):
        from products.models import Category
        context = {
            'category_list': Category.on_site.filter(pk__in=[35, 390, 253, 418, 2700, 2713, 172, 126, 323]),
            'breadcrumbs': self.breadcrumbs,
        }
        context.update(super(BreadcrumbsMixin, self).get_context_data(**kwargs))
        return context
