# -*- coding: utf-8 -*-
from django.conf import settings
from django.template import Library, Node

register = Library()

PAGINATION_WINDOW = getattr(settings, 'PAGINATION_WINDOW', 10)


class PaginationNode(Node):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def render(self, context):
        is_paginated = context.get('is_paginated')
        if is_paginated:
            pages = context['paginator'].num_pages
            page = context['page_obj'].number
        
            pagination_window = self.kwargs.get('by', PAGINATION_WINDOW)
            window = int(pagination_window / 2)
            if(page <= window):
                page_range = [n for n in range(1, pagination_window + 1) if n <= pages]
            else:
                page_range = [n for n in range(page - window, page + window) if n > 0 and n <= pages]
        
            context.update({
              "page_range": page_range,
            })
        return ''
    

@register.tag
def pagination(parser, token):
    tokens = iter(token.split_contents()[1:])
    kwargs = {token: tokens.next() for token in tokens}
    return PaginationNode(**kwargs)
