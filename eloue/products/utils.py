# -*- coding: utf-8 -*-

from django.utils.text import wrap
from django.utils.translation import ugettext_lazy as _


def format_quote(sender, body):
    """
    Wraps text at 55 chars and prepends each
    line with `> `.
    Used for quoting messages in replies.
    """
    lines = wrap(body, 55).split('\n')
    for i, line in enumerate(lines):
        lines[i] = "> %s" % line
    quote = '\n'.join(lines)
    return _(u"\n\n\n\n\n%(sender)s wrote:\n%(body)s") % {
        'sender': sender,
        'body': quote,
        }
            
def escape_percent_sign(unescaped_url):
    """
    Escapes standalone percent signs in raw url's, like localhost:8000/location/jardinage?q=ch%C3%A8vre&sort=price
    """
    return unescaped_url.replace('%', '%%')
