from django.template import Library

register = Library()

@register.simple_tag
def active(request, pattern, option=''):
    import re
    if re.search('%s%s' % (pattern, option), request.path):
        return 'selected-nav-bar-link'
    return ''