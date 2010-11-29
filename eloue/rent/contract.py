# -*- coding: utf-8 -*-
import os

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from pyPdf import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas

from django.utils.dateformat import format
from django.utils.encoding import force_unicode

from eloue.rent.utils import spellout

local_path = lambda path: os.path.join(os.path.dirname(__file__), path)


class ContractGenerator(object):
    def __call__(self, booking):
        """Merge template and carbon to produce final contract"""
        template = self.load_template(booking)
        carbon = self.generate_carbon(booking)
        contract_final = PdfFileWriter()
        for i in range(template.getNumPages()):
            page = template.getPage(i)
            if i < carbon.getNumPages():
                page.mergePage(carbon.getPage(i))
            contract_final.addPage(page)
        contract_file = StringIO()
        contract_final.write(contract_file)
        return contract_file
    
    def load_template(self, booking):
        """Load template pdf"""
        return PdfFileReader(open(local_path("contract/standard_template.pdf")))
    
    def generate_carbon(self, booking):
        "Create and draw the carbon"
        carbon_file = StringIO()
        carbon = canvas.Canvas(carbon_file)
        carbon = self.draw(carbon, booking)
        carbon.save()
        return PdfFileReader(carbon_file)
    
    def draw(self, canvas, booking):
        """Draw stuff in the carbon"""
        from django.utils.timesince import timesince
        canvas.setFont("Helvetica", 10)
        # Owner coordinates
        if booking.owner.is_professional:
            canvas.drawString(71, 633, booking.owner.company_name)
        else:
            canvas.drawString(71, 633, booking.owner.get_full_name())
        address = booking.owner.addresses.all()[0]
        canvas.drawString(71, 573, address.address1)
        canvas.drawString(71, 563, "%s %s - %s" % (address.zipcode, address.city, address.country))
        phone = booking.owner.phones.all()[0]
        canvas.drawString(71, 543, phone.number)
        
        # Borrower coordinates
        if booking.borrower.is_professional:
            canvas.drawString(71, 333, booking.borrower.company_name)
        else:
            canvas.drawString(71, 333, booking.borrower.get_full_name())
        address = booking.borrower.addresses.all()[0]
        canvas.drawString(71, 273, address.address1)
        canvas.drawString(71, 263, "%s %s - %s" % (address.zipcode, address.city, address.country))
        phone = booking.borrower.phones.all()[0]
        canvas.drawString(71, 243, phone.number)
        
        # Change page
        canvas.showPage()
        canvas.setFont("Helvetica", 10)
        
        # Product related
        canvas.drawString(71, 582, booking.product.summary)
        canvas.drawString(225, 345, "%s." % timesince(booking.started_at, booking.ended_at))
        canvas.drawString(245, 313, format(booking.started_at, "%d %F %Y à %Hh%M."))
        canvas.drawString(198, 282, format(booking.ended_at, "%d %F %Y à %Hh%M."))
        canvas.drawString(166, 220, "%s %s." % (booking.total_amount, booking.currency))
                
        # Change page
        canvas.showPage()
        canvas.setFont("Helvetica", 10)
        
        spelled_number = spellout(booking.deposit_amount, unit='euro', decimal='cent')
        canvas.drawString(71, 640, "%s %s / %s" % (booking.deposit_amount, booking.currency, force_unicode(spelled_number)))
        return canvas
    
