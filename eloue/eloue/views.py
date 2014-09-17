# -*- coding: utf-8 -*-
from django import http
from django.views.decorators.csrf import requires_csrf_token
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import View, TemplateView
from django.template import RequestContext, loader
from django.db.models import Count

from products.forms import FacetedSearchForm
from products.models import Product

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
    return http.HttpResponseNotFound(
    	t.render(RequestContext(request, {'request_path': request.path, 'form': form}))
    )

class LoginRequiredMixin(View):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)

class HomepageView(TemplateView):
    template_name = 'index.jade'

    def get_context_data(self, **kwargs):
        product_stats = Product.objects.extra(
            tables=['accounts_address'],
            where=['"products_product"."address_id" = "accounts_address"."id"'],
            select={'city': 'lower(accounts_address.city)'}
        ).values('city').annotate(Count('id')).order_by('-id__count')
        context = super(HomepageView, self).get_context_data(cities_list=product_stats, **kwargs)
        return context
