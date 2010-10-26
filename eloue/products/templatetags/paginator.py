# -*- coding: utf-8 -*-
from django.template import Library

register = Library()

DOT = '.'

@register.inclusion_tag('products/pagination.html', takes_context=True)
def pagination(context):
    paginator = context['paginator']
    page_obj = context['page_obj']
    
    ON_EACH_SIDE = 3
    ON_ENDS = 2
    
    # If there are 10 or fewer pages, display links to every page.
    # Otherwise, do some fancy
    if paginator.num_pages <= 10:
        page_range = range(paginator.num_pages)
    else:
        # Insert "smart" pagination links, so that there are always ON_ENDS
        # links at either end of the list of pages, and there are always
        # ON_EACH_SIDE links at either end of the "current page" link.
        page_range = []
        if page_obj.number > (ON_EACH_SIDE + ON_ENDS):
            page_range.extend(range(0, ON_EACH_SIDE - 1))
            page_range.append(DOT)
            page_range.extend(range(page_obj.number - ON_EACH_SIDE, page_obj.number + 1))
        else:
            page_range.extend(range(0, page_obj.number + 1))
            if page_obj.number < (paginator.num_pages - ON_EACH_SIDE - ON_ENDS - 1):
                page_range.extend(range(page_obj.number + 1, page_obj.number + ON_EACH_SIDE + 1))
                page_range.append(DOT)
                page_range.extend(range(paginator.num_pages - ON_ENDS, paginator.num_pages))
            else:
                page_range.extend(range(page_obj.number + 1, paginator.num_pages))

    context.update({ 'page_range': [ page + 1 if isinstance(page, int) else page for page in page_range ] })
    return context
