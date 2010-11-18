# -*- coding: utf-8 -*-
from django.conf import settings
from django.template import Library, Node

register = Library()

PAGINATION_WINDOW = getattr(settings, 'PAGINATION_WINDOW', 10)


class PaginationNode(Node):
    def render(self, context):
        is_paginated = context['is_paginated']
        if is_paginated:
            pages = context['pages']
            page = context['page']
        
            window = int(PAGINATION_WINDOW / 2)
            if(page <= window):
                page_range = [n for n in range(1, page + PAGINATION_WINDOW) if n > 0 and n <= pages]
            else:
                page_range = [n for n in range(page - window, page + window) if n > 0 and n <= pages]
        
            context.update({
              "page_range": page_range,
            })
        return ''
    

@register.tag
def pagination(parser, token):
    return PaginationNode()
