# -*- coding: utf-8 -*-
from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.utils.translation import ugettext_lazy as _
from django.utils.datastructures import SortedDict

from haystack.query import SearchQuerySet
from haystack.constants import DJANGO_ID

from products.forms import FacetedSearchForm
from eloue.http import JsonResponse
from products.search import product_search
from eloue.search_backends import is_algolia
from django.views.generic.base import RedirectView
from django.core.urlresolvers import reverse


class LoginRequiredMixin(View):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


class SearchQuerySetMixin(object):
    def dispatch(self, request, *args, **kwargs):
        self.sqs = kwargs.pop('sqs', None) or product_search
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
            if is_algolia(): #FIXME move into EloueAlgoliaSearchQuery
                queryset = queryset.filter(**{"django_id_int": int(pk)})
            else:
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

        if obj.object is None:
            raise Http404(_(
                'Product with pk %(pk)s and slug "%(slug)s" does not exist') %
                {'pk': pk,
                 'slug': slug, })

        return obj


class AjaxResponseMixin(object):
    response_class = JsonResponse

    def render_to_response(self, context, **kwargs):
        return self.response_class(context, **kwargs)


class BreadcrumbsMixin(object):
    form_class = FacetedSearchForm

    def get_form(self, request):
        location = request.session.setdefault('location', settings.DEFAULT_LOCATION)
        query_data = request.GET.copy()
        if 'l' not in query_data or not query_data['l']:
            if settings.DEFAULT_LOCATION_CITY:
                query_data['l'] = settings.DEFAULT_LOCATION_CITY['city']
                query_data['r'] = settings.DEFAULT_LOCATION_CITY['radius']
            else:
                query_data['l'] = location['country']
        form = self.form_class(query_data)
        return form

    def get_breadcrumbs(self, request):
        form = self.get_form(request)
        if not form.is_valid():
            raise Http404
        self.form = form

        breadcrumbs = SortedDict()
        breadcrumbs['q'] = {'name': 'q', 'value': form.cleaned_data.get('q', None), 'label': 'q', 'facet': False}
        breadcrumbs['sort'] = {'name': 'sort', 'value': form.cleaned_data.get('sort', None), 'label': 'sort', 'facet': False}
        breadcrumbs['l'] = {'name': 'l', 'value': form.cleaned_data.get('l', None), 'label': 'l', 'facet': False}
        breadcrumbs['r'] = {'name': 'r', 'value': form.cleaned_data.get('r', None), 'label': 'r', 'facet': False}
        breadcrumbs['renter'] = {'name': 'renter', 'value': form.cleaned_data.get('renter'), 'label': 'renter', 'facet': False}
        return breadcrumbs

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(self, 'breadcrumbs'):
            self.breadcrumbs = self.get_breadcrumbs(request)
        return super(BreadcrumbsMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = {
            'breadcrumbs': self.breadcrumbs,
        }
        context.update(super(BreadcrumbsMixin, self).get_context_data(**kwargs))
        return context
    
    
class ImportedObjectRedirectView(RedirectView):
    
    permanent = True
    
    model = None
    origin = None
    fallback_pattern_name = None
    filter_key = 'original_id'
    convert = lambda self,x:x
    
    def get_redirect_url(self, *args, **kwargs):
        field_name = self.filter_key.split('__', 1)[0]
        get_kwargs = {'import_record__origin__iexact':self.origin, 
                      self.filter_key:self.convert(kwargs[field_name])}
        try:
            obj = self.model.objects.get(**get_kwargs)
            return obj.get_absolute_url()
        except self.model.DoesNotExist:
            return reverse(self.fallback_pattern_name)
            

