import pytest
from django.core.urlresolvers import reverse
from rest_framework.status import HTTP_200_OK
from django.contrib import messages
from products.admin import ProductAdmin
from django.contrib.admin.models import LogEntry
from django.test.client import Client


@pytest.fixture()
def eloue_user(db, django_user_model):
        return django_user_model._default_manager.create_user(
            username='test',
            email='test@example.com',
            password='test')
        
        
@pytest.fixture()
def eloue_admin_user(db, django_user_model, django_username_field):

    UserModel = django_user_model
    
    try:
        user = UserModel._default_manager.get(**{django_username_field: 'admin'})
    except UserModel.DoesNotExist:
        user = UserModel._default_manager.create_superuser(
            'admin', 'admin@example.com', 'password')
    return user


@pytest.fixture()
def eloue_admin_client(db, eloue_admin_user):
    
    client = Client()
    client.login(username=eloue_admin_user.email, password='password')
    return client


class TestProductAdmin(object):
    
    def test_update_index_permissions(self, eloue_user, client, eloue_admin_client):
            
        resp = client.get(reverse('admin:update_product_index'), follow=True)
        assert resp.status_code == HTTP_200_OK
        assert resp.template_name == "admin/login.html"
        
        client.login(username=eloue_user.email, password=eloue_user.password)
        r = client.get(reverse('admin:update_product_index'), follow=True)
        assert r.status_code == HTTP_200_OK
        assert resp.template_name == "admin/login.html"
        
        resp = eloue_admin_client.get(reverse('admin:update_product_index'), follow=True)
        assert resp.status_code == HTTP_200_OK
        assert resp.template_name == 'admin/products/change_list.html'

    
    @pytest.mark.xfail(reason="this passed because queue is not empty without adding products")
    def test_update_index_command_succeeded(self, eloue_admin_client):   

        lc = LogEntry.objects.count()
        resp = eloue_admin_client.get(reverse('admin:update_product_index'), follow=True)
        assert resp.status_code == HTTP_200_OK
        assert resp.template_name == 'admin/products/change_list.html'
        assert len(resp.context['messages']) == 1
        m = resp.context['messages'].__iter__().next()
        assert m.level == messages.SUCCESS
        assert m.message == ProductAdmin.MESSAGE_REINDEX_SUCCESS
        assert LogEntry.objects.count() == lc + 1
        

    def test_update_index_command_failed(self, eloue_admin_client, 
                                             monkeypatch):
        
        message = "Some reason"
        def fake_handle_updates(self):
            raise Exception(message)
        
        monkeypatch.setattr('queued_search.management.commands'+
                        '.process_search_queue.Command.handle_updates',fake_handle_updates)
        
        resp = eloue_admin_client.get(reverse('admin:update_product_index'), follow=True)
        assert resp.status_code == HTTP_200_OK
        assert resp.template_name == 'admin/products/change_list.html'
        assert len(resp.context['messages']) == 1
        m = resp.context['messages'].__iter__().next()
        assert m.level == messages.ERROR
        assert m.message == message
        
