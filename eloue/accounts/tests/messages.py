import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from eloue.accounts.models import Patron
from django_messages.models import Message

class SendTestCase(TestCase):
    
    
    def setUp(self):
        self.user1 = Patron(username='user1', password='123456', email='user1@example.com')
        self.user1.save()
        self.user2 = Patron(username='user2', password='123456', email='user2@example.com')
        self.user2.save()
        
    def test_content_filter(self):
        
        body_before = """this is my phone number: 0678987890, +33687898765, 06 87 98 54 67
        this is my email: lin.liu@e-loue.com, linliu@sds.com, linliu@oioi.coms"""
        msg1 = Message(sender=self.user1, recipient=self.user2, subject='test of content filter', body=body_before)
        msg1.save()
        body_after = """this is my phone number: ########, ########, ########
        this is my email: ########, ########, ########"""
        self.assertEquals(msg1.body, body_after)
        
    def test_site_filter(self):
        
        # ok case
        msg1 = Message(sender=self.user1, recipient=self.user2, subject='test of site filter', body="test site")
        msg1.save()
        self.assertEquals(msg1.recipient, self.user2)
        
        # ko case
        user_uk = Patron(username="uk_user", password="123", email="lin.liu@gmail.com") 
        user_uk.save()
        user_uk.sites.clear()
        msg2 = Message(sender=self.user1, recipient=user_uk, subject='test of site filter', body="test site")
        msg2.save()
        self.assertEquals(msg2.recipient, None)
        
    def test_patron_user_cmp(self):
        user = User.objects.get(username="user1")
        self.assertTrue(isinstance(user, User))
        self.assertTrue(isinstance(self.user1, Patron))
        self.assertTrue(user==self.user1)
        
    def tearDown(self):
        self.user1.delete()
        self.user2.delete()
        
        