# -*- coding: utf-8 -*-

from lxml import etree
import requests

from django.conf import settings

def viva_check_phone(
    phone_number, client_id=None, request=None,
    site_id=None, url='http://mer.viva-multimedia.com/v2/xmlRequest.php',
    timeout=2.0
):
    # validate arguments
    if client_id is None and request:
        client_id = ''.join([request.META['REMOTE_ADDR'], request.META['HTTP_USER_AGENT']])
    if site_id is None:
        site_id = getattr(settings, 'VIVA_SITE_ID', '')

    # construct XML DOM tree for request
    generate = etree.Element('generate')
    siteId = etree.SubElement(generate, 'siteId')
    siteId.text = site_id
    idClient = etree.SubElement(generate, 'idClient')
    idClient.text = client_id
    number = etree.SubElement(generate, 'numero')
    number.text = phone_number
    country = etree.SubElement(generate, 'pays')
    country.text = 'FR'

    # generate XML document from DOM tree
    xml = etree.tostring(generate, xml_declaration=True, encoding='UTF-8')

    # perform network request to remote service
    res = requests.post(url, data={'xml': xml}, timeout=timeout)

    # check response's status code and raise and exception if it is not OK
    if res.status_code != 200:
        res.raise_for_status()

    # parse response's XML
    root = etree.fromstring(res.content)
    # create a key-value dictionary where keys are tag names, and values are tag texts
    tags = {
        elem.tag: elem.text.strip()
        for elem in root.iter(tag=etree.Element)
        if elem.text and elem.text.strip()
    }
    # return the created dictionary as the result
    return tags
