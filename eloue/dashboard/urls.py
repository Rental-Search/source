# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

from eloue.accounts.views import dashboard, patron_edit, patron_edit_password, patron_edit_phonenumber,\
									patron_edit_addresses, accounts_work_autocomplete, accounts_studies_autocomplete, comments,\
									comments_received, owner_booking_pending, owner_booking_ongoing, owner_booking_history, owner_booking_authorized, alert_edit, owner_product, \
                                    associate_facebook, facebook_invite, gmail_invite
from eloue.products.views import product_edit, product_address_edit, product_price_edit, thread_details, archive_thread, unarchive_thread, inbox, archived
from eloue.rent.views import booking_detail, booking_accept, booking_cancel, booking_reject, booking_incident, booking_close

urlpatterns = patterns('',
	url(r'^profil/$', dashboard, name="dashboard"),
    url(r'^account/$', patron_edit, name="patron_edit"),
    url(r'^account/password/$', patron_edit_password, name="patron_edit_password"),
    url(r'^account/phonenumbers/$', patron_edit_phonenumber, name="patron_edit_phonenumber"),
    url(r'^account/addresses/$', patron_edit_addresses, name="patron_edit_addresses"),
    url(r'^account/credit_card/$', 'eloue.accounts.views.patron_edit_credit_card', name="patron_edit_credit_card"),
    url(
        r'^account/credit_card/delete/$', 
        'eloue.accounts.views.patron_delete_credit_card', 
        name="patron_delete_credit_card"
    ),
    url(r'^account/rib/$', 'eloue.accounts.views.patron_edit_rib', name='patron_edit_rib'),
    
    url(r'^account/accounts_work_autocomplete$', accounts_work_autocomplete, name='accounts_work_autocomplete'),
    url(r'^account/accounts_studies_autocomplete/$', accounts_studies_autocomplete, name='accounts_studies_autocomplete'),
    url(r'^account/comments/$', comments, name="comments"),
    url(r'^account/comments_received/$', comments_received, name="comments_received"),

    url(r'^account/invite/facebook/$', facebook_invite, name="facebook_invite"),
    url(r'^account/invite/gmail/$', gmail_invite, name="gmail_invite"),

    url(r'^owner/booking/authorized/$', owner_booking_authorized, name="owner_booking_authorized"),
    url(r'^owner/booking/authorized/(?P<page>\d+)/$', owner_booking_authorized, name="owner_booking_authorized"),
    url(r'^owner/booking/pending/$', owner_booking_pending, name="owner_booking_pending"),
    url(r'^owner/booking/pending/(?P<page>\d+)/$', owner_booking_pending, name="owner_booking_pending"),
    url(r'^owner/booking/ongoing/$', owner_booking_ongoing, name="owner_booking_ongoing"),
    url(r'^owner/booking/ongoing/(?P<page>\d+)/$', owner_booking_ongoing, name="owner_booking_ongoing"),
    url(r'^owner/booking/history/$', owner_booking_history, name="owner_booking_history"),
    url(r'^owner/booking/history/(?P<page>\d+)/$', owner_booking_history, name="owner_booking_history"),
    # url(r'^owner/history/$', owner_history, name="owner_history"),
    # url(r'^owner/history/page/(?P<page>\d+)/$', owner_history, name="owner_history"),
    url(r'^owner/product/$', owner_product, name="owner_product"),
    url(r'^owner/product/page/(?P<page>\d+)/$', owner_product, name="owner_product"),
    url(r'^owner/product/(?P<slug>[-\w]+)-(?P<product_id>\d+)/$', product_edit, name="owner_product_edit"),
    url(r'^owner/product/(?P<slug>[-\w]+)-(?P<product_id>\d+)/address/$', product_address_edit, name="owner_product_address_edit"),
    url(r'^owner/product/(?P<slug>[-\w]+)-(?P<product_id>\d+)/price/$', product_price_edit, name="owner_product_price_edit"),
    url(r'^alertes/$', alert_edit, name="alert_edit"),
    url(r'^borrower/booking/pending/$', 'eloue.accounts.views.borrower_booking_pending', name="borrower_booking_pending"),
    url(r'^borrower/booking/ongoing/$', 'eloue.accounts.views.borrower_booking_ongoing', name="borrower_booking_ongoing"),
    url(r'^borrower/booking/authorized/$', 'eloue.accounts.views.borrower_booking_authorized', name="borrower_booking_authorized"),
    url(r'^borrower/booking/history/$', 'eloue.accounts.views.borrower_booking_history', name="borrower_booking_history"),
    url(r'^borrower/booking/pending/(?P<page>\d+)/$', 'eloue.accounts.views.borrower_booking_pending', name="borrower_booking_pending"),
    url(r'^borrower/booking/ongoing/(?P<page>\d+)/$', 'eloue.accounts.views.borrower_booking_ongoing', name="borrower_booking_ongoing"),
    url(r'^borrower/booking/authorized/(?P<page>\d+)/$', 'eloue.accounts.views.borrower_booking_authorized', name="borrower_booking_authorized"),
    url(r'^borrower/booking/history/(?P<page>\d+)/$', 'eloue.accounts.views.borrower_booking_history', name="borrower_booking_history"),
    url(r'^booking/(?P<booking_id>[0-9a-f]{32})/$', booking_detail, name="booking_detail"),
    url(r'^booking/(?P<booking_id>[0-9a-f]{32})/comment/$', 'eloue.accounts.views.comment_booking', name="comment_booking"),
    url(r'^booking/(?P<booking_id>[0-9a-f]{32})/view_comment/$', 'eloue.accounts.views.view_comment', name="view_comment"),
    url(r'^booking/(?P<booking_id>[0-9a-f]{32})/accept/$', booking_accept, name="booking_accept"),
    url(r'^booking/(?P<booking_id>[0-9a-f]{32})/cancel/$', booking_cancel, name="booking_cancel"),
    url(r'^booking/(?P<booking_id>[0-9a-f]{32})/reject/$', booking_reject, name="booking_reject"),
    url(r'^booking/(?P<booking_id>[0-9a-f]{32})/incident/$', booking_incident, name="booking_incident"),
    url(r'^booking/(?P<booking_id>[0-9a-f]{32})/close/$', booking_close, name="booking_close"),
    url(r'^booking/(?P<booking_id>[0-9a-f]{32})/contract/$', 'eloue.rent.views.booking_contract', name="booking_contract"),
    #url(r'^messages/(?P<message_id>[\d]+)/reply/$', reply_product_related_message, name='reply_product_related_message'),
    url(r'^messages/(?P<thread_id>[\d]+)$', thread_details, name='thread_details'),
    url(r'^messages/(?P<thread_id>[\d]+)/archive/$', archive_thread, name='archive_thread'),
    url(r'^messages/(?P<thread_id>[\d]+)/unarchive/$', unarchive_thread, name='unarchive_thread'),
    url(r'^messages/inbox', inbox, name='inbox'),
    url(r'^messages/archived', archived, name='archived'),
    url(r'^messages/', include('django_messages.urls')),	
)