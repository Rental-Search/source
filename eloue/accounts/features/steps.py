# -*- coding: utf-8 -*-
from freshen import *

from django.core import mail
from django.core.urlresolvers import reverse
from django.utils.encoding import smart_str
from django.test.client import Client

from eloue.checks import *

@Before
def before(sc):
    scc.client = Client()
    scc.response = None
    scc.form = {}
    scc.fixtures = ['patron']

@Given("I fill '(.*)' field with '(.*)'")
def fill(field, value):
    scc.form[field] = value

@When("I navigate to '(.*)'")
def navigation(url):
    scc.response = scc.client.get(url)

@When("I navigate to page '(.*)'")
def navigation_reverse(name):
    scc.response = scc.client.get(reverse(name))

@When("I submit to '(.*)'")
def submit(url):
    scc.response = scc.client.post(url, scc.body)

@When("I submit to page '(.*)'")
def submit_reverse(name):
    scc.response = scc.client.post(reverse(name), scc.form)
    scc.form = {}

@Then("I should find '(.*)'")
def contains(text):
    assert_contains(scc.response, text)

@Then("I should have received (\d+) email[s]?")
def inbox(count):
    assert_equals(len(mail.outbox), int(count))

@Then("I should be redirected to page '(.*)'( with code (\d{3}))?")
def redirect_reverse(name, *args):
    code = args[1] or 301
    assert_redirects(scc.response, reverse(name), status_code=int(code))
