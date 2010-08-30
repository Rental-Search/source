# -*- coding: utf-8 -*-
import re

def spelling_suggestion(search_queryset):
    suggestions = search_queryset.spelling_suggestion()
    if suggestions:
        match = re.match('\(site:[\d]+ AND (.*)\)', suggestions)
        suggestions = match.groups()[0] if match else None
        suggestions = re.sub('AND\s*', '', suggestions) if suggestions else None
    return suggestions or None
