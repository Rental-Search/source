# -*- coding: utf-8 -*-
import random
from datetime import datetime, timedelta

from freshen import *

from django.core import mail
from django.core.urlresolvers import reverse
from django.test.client import Client

from eloue.checks import *
from accounts.models import Patron


@Before
def before(sc):
    scc.client = Client()
    scc.response = None
    scc.form = {}
    scc.fixtures = ['patron']


@Given("I am user (.*)")
def user(username):
    scc.user = Patron.objects.get(username=username)
    scc.password = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz', random.randint(5, 15)))
    scc.user.set_password(scc.password)
    scc.user.save()


@Given("my account is (inactive|active)")
def activated(status):
    scc.user.is_active = (status == 'active')
    scc.user.save()


@Given("I fill '(.*)' field with '(.*)'")
def fill(field, value):
    scc.form[field] = value


@Given("I've created my account (\d+) days ago")
def joined_at(days):
    scc.user.date_joined = datetime.now() - timedelta(days=int(days))
    scc.user.save()


@When("I activate my account")
def activate():
    scc.response = scc.client.get(reverse('auth_activate', args=[scc.user.activation_key]))
    assert_equals(scc.response.status_code, 200)


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


@Then("I should( not)? be able to login")
def test_login(negative):
    logged = scc.client.login(username=scc.user.email, password=scc.password)
    if not negative:
        assert_true(logged)
    else:
        assert_false(logged)


@Then("I should see a (error|welcome) message")
def message(status):
    if status == 'welcome':
        assert_true(isinstance(scc.response.context['is_actived'], Patron))
    else:
        assert_true(scc.response.context['is_actived'] == False)
