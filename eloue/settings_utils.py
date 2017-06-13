# -*- coding: utf-8 -*-

def algolia_category_attributes(lang):
    """
    :param lang: language code
    :return: list with attribute names for one language
    """
    return [
        'algolia_categories.%s.lvl0' % lang,
        'algolia_categories.%s.lvl1' % lang,
        'algolia_categories.%s.lvl2' % lang,
    ]


def algolia_category_attributes_for_faceting(langs):
    """
    :param langs: LANGUAGES setting
    :return: list with attribute names for all languages
    """
    return [attr
        for lang,_ in langs
        for attr in algolia_category_attributes(lang)]


def agolia_category_facet_name(lang):
    lang = lang.split('-')[0] if '-' in lang else lang
    return 'category.%s' % lang


def algolia_category_facets(langs):
    """
    :param langs: LANGUAGES setting
    :return: facet dicts
    """
    return [{
        'name': agolia_category_facet_name(lang),
        'attributes': algolia_category_attributes(lang),
        'sortBy': ['name:asc']
    } for lang,_ in langs]