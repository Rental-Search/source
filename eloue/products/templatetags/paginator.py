# -*- coding: utf-8 -*-
from django.template import Library

register = Library()

LEADING_PAGE_RANGE_DISPLAYED = TRAILING_PAGE_RANGE_DISPLAYED = 4
LEADING_PAGE_RANGE = TRAILING_PAGE_RANGE = 2
NUM_PAGES_OUTSIDE_RANGE = 2 
ADJACENT_PAGES = 2


@register.inclusion_tag('products/pagination.html', takes_context=True)
def pagination(context):
    is_paginated = context['is_paginated']
    if is_paginated:
        in_leading_range = in_trailing_range = False
        pages_outside_leading_range = pages_outside_trailing_range = range(0)
        pages = context['pages']
        page = context['page']
        
        if (pages <= LEADING_PAGE_RANGE_DISPLAYED):
            in_leading_range = in_trailing_range = True
            page_range = [n for n in range(1, pages + 1) if n > 0 and n <= pages]           
        elif (page <= LEADING_PAGE_RANGE):
            in_leading_range = True
            page_range = [n for n in range(1, LEADING_PAGE_RANGE_DISPLAYED + 1) if n > 0 and n <= pages]
            pages_outside_leading_range = [n + pages for n in range(0, -NUM_PAGES_OUTSIDE_RANGE, -1)]
        elif (page > pages - TRAILING_PAGE_RANGE):
            in_trailing_range = True
            page_range = [n for n in range(pages - TRAILING_PAGE_RANGE_DISPLAYED + 1, pages + 1) if n > 0 and n <= pages]
            pages_outside_trailing_range = [n + 1 for n in range(0, NUM_PAGES_OUTSIDE_RANGE)]
        else: 
            page_range = [n for n in range(page - ADJACENT_PAGES, page + ADJACENT_PAGES + 1) if n > 0 and n <= pages]
            pages_outside_leading_range = [n + pages for n in range(0, -NUM_PAGES_OUTSIDE_RANGE, -1)]
            pages_outside_trailing_range = [n + 1 for n in range(0, NUM_PAGES_OUTSIDE_RANGE)]
        context.update({
          "page_range":page_range,
          "in_leading_range" : in_leading_range,
          "in_trailing_range" : in_trailing_range,
          "pages_outside_leading_range": pages_outside_leading_range,
          "pages_outside_trailing_range": pages_outside_trailing_range  
        })
    return context
