# -*- coding: utf-8 -*-
from django.contrib import admin

from eloue.rent.models import Booking

class BookingAdmin(admin.ModelAdmin):
    pass

admin.site.register(Booking, BookingAdmin)