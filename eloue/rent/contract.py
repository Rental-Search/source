# -*- coding: utf-8 -*-
import os

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from pyPdf import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas

from django.conf import settings
from django.utils.dateformat import format
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _

from eloue.rent.utils import spellout

local_path = lambda path: os.path.join(os.path.dirname(__file__), path)


class ContractGeneratorNormal(object):
    templates = {
        'fr-fr': local_path("contract/fr_template.pdf"),
        'en-uk': local_path("contract/uk_template.pdf"),
    }
    templates = {
        'fr-fr': local_path("contract/fr_template_normal.pdf")
    }
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
        return PdfFileReader(open(self.templates[settings.LANGUAGE_CODE]))

    def generate_carbon(self, booking):
        "Create and draw the carbon"
        carbon_file = StringIO()
        carbon = canvas.Canvas(carbon_file)
        carbon = self.draw(carbon, booking)
        carbon.save()
        return PdfFileReader(carbon_file)
    
    def draw(self, canvas, booking):
        """Draw stuff in the carbon"""
        canvas.setFont("Helvetica", 10)
        canvas.drawString(99, 614, u"{first_name} {last_name}".format(
                first_name=booking.borrower.first_name, 
                last_name=booking.borrower.last_name.upper()
            )
        )
        canvas.drawString(83, 603, u"{phone}".format(phone=booking.borrower.phones.all()[0]))
        canvas.drawString(75, 594, u"{address1}".format(address1=booking.borrower.default_address or booking.borrower.addresses.all()[0]))
        # canvas.drawString(135, 575, "{date_of_birth}, {place_of_birth}".format(
        #         date_of_birth=booking.borrower.date_of_birth.strftime("%d/%m/%Y"),
        #         place_of_birth=booking.borrower.place_of_birth
        #     )
        # )
        # canvas.drawString(115, 540, "{masked_number}".format(
        #     masked_number=booking.borrower.creditcard.masked_number
        # ))
        # canvas.drawString(115, 530, "{expires}".format(
        #     expires=booking.borrower.creditcard.expires
        # ))
        canvas.drawString(170, 438, "{started_at}".format(started_at=booking.started_at.strftime("%d/%m/%Y à %H:%M")))
        canvas.drawString(176, 426, "{ended_at}".format(ended_at=booking.ended_at.strftime("%d/%m/%Y à %H:%M")))
        canvas.drawString(180, 415, "{total_amount} {currency}.".format(total_amount=booking.total_amount, currency=booking.currency))

        canvas.drawString(430, 660, "{first_name} {last_name}".format(
            first_name=booking.owner.first_name,
            last_name=booking.owner.last_name.upper()
        ))
        canvas.drawString(430, 644, "{phone}".format(phone=booking.owner.phones.all()[0]))
        canvas.drawString(430, 570, "{summary}".format(summary=booking.product.summary))
        return canvas


class ContractGeneratorCar(ContractGeneratorNormal):
    templates = {
        'fr-fr': local_path("contract/fr_template_car.pdf"),
        'en-uk': local_path("contract/uk_template.pdf"),
    }
    def draw(self, canvas, booking):
        canvas.setFont("Helvetica", 10)
        canvas.drawString(0, 0, "0,0 -----")
        canvas.drawString(10, 10, "10,10 -----")
        canvas.drawString(0, 100, "0,100 -----")
        canvas.drawString(100, 0, "100,0 -----")
        canvas.drawString(200, 0, "200,0 -----")
        canvas.drawString(300, 0, "300,0 -----")
        canvas.drawString(400, 0, "400,0 -----")
        canvas.drawString(500, 0, "500,0 -----")
        canvas.drawString(0, 100, "0,100 -----")
        canvas.drawString(0, 200, "0,200 -----")
        canvas.drawString(0, 300, "0,300 -----")
        canvas.drawString(0, 400, "0,400 -----")
        canvas.drawString(0, 500, "0,500 -----")
        canvas.drawString(0, 600, "0,600 -----")
        canvas.drawString(0, 700, "0,700 -----")
        canvas.drawString(0, 800, "0,800 -----")
        canvas.drawString(0, 900, "0,900 -----")
        canvas.drawString(85, 764, "{first_name} {last_name}".format(
                first_name=booking.borrower.first_name, 
                last_name=booking.borrower.last_name.upper()
            )
        )
        canvas.drawString(72, 752, "{phone}".format(phone=booking.borrower.phones.all()[0]))
        canvas.drawString(70, 741, "{address1}".format(address1=booking.borrower.default_address or booking.borrower.addresses.all()[0]))
        canvas.drawString(120, 720, "{date_of_birth}, {place_of_birth}".format(
                date_of_birth=booking.borrower.date_of_birth.strftime("%d/%m/%Y"),
                place_of_birth=booking.borrower.place_of_birth
            )
        )
        canvas.drawString(115, 710, "{drivers_license_number}".format(
                drivers_license_number=booking.borrower.drivers_license_number
            )
        )
        canvas.drawString(130, 700, "{drivers_license_date}".format(
            drivers_license_date=booking.borrower.drivers_license_date.strftime("%d/%m/%Y")
        ))
        canvas.drawString(115, 640, "{masked_number}".format(
            masked_number=booking.borrower.creditcard.masked_number
        ))
        canvas.drawString(115, 630, "{expires}".format(
            expires=booking.borrower.creditcard.expires
        ))
        canvas.drawString(170, 535, "{started_at}".format(started_at=booking.started_at.strftime("%d/%m/%Y à %H:%M")))
        canvas.drawString(175, 522, "{ended_at}".format(ended_at=booking.ended_at.strftime("%d/%m/%Y à %H:%M")))
        canvas.drawString(168, 490, "{total_amount}".format(total_amount=booking.total_amount))

        canvas.drawString(430, 760, "{first_name} {last_name}".format(
            first_name=booking.owner.first_name,
            last_name=booking.owner.last_name.upper()
        ))
        canvas.drawString(430, 744, "{phone}".format(phone=booking.owner.phones.all()[0]))
        canvas.drawString(430, 710, "{summary}".format(summary=booking.product.summary))
        canvas.drawString(430, 693, "{licence_plate}".format(licence_plate=booking.product.carproduct.licence_plate))
        canvas.drawString(430, 680, "{first_registration_date}".format(first_registration_date=booking.product.carproduct.first_registration_date))
        return canvas
        

class ContractGeneratorRealEstate(ContractGeneratorNormal):
    templates = {
        'fr-fr': local_path("contract/fr_template_realestate.pdf"),
        'en-uk': local_path("contract/uk_template.pdf"),
    }
    def draw(self, canvas, booking):
        """Draw stuff in the carbon"""
        canvas.setFont("Helvetica", 10)
        canvas.drawString(99, 614, "{first_name} {last_name}".format(
                first_name=booking.borrower.first_name, 
                last_name=booking.borrower.last_name.upper()
            )
        )
        canvas.drawString(83, 603, "{phone}".format(phone=booking.borrower.phones.all()[0]))
        canvas.drawString(75, 594, "{address1}".format(address1=booking.borrower.default_address or booking.borrower.addresses.all()[0]))
        canvas.drawString(135, 575, "{date_of_birth}, {place_of_birth}".format(
                date_of_birth=booking.borrower.date_of_birth.strftime("%d/%m/%Y"),
                place_of_birth=booking.borrower.place_of_birth
            )
        )
        canvas.drawString(115, 540, "{masked_number}".format(
            masked_number=booking.borrower.creditcard.masked_number
        ))
        canvas.drawString(115, 530, "{expires}".format(
            expires=booking.borrower.creditcard.expires
        ))
        canvas.drawString(170, 438, "{started_at}".format(started_at=booking.started_at.strftime("%d/%m/%Y à %H:%M")))
        canvas.drawString(176, 426, "{ended_at}".format(ended_at=booking.ended_at.strftime("%d/%m/%Y à %H:%M")))
        canvas.drawString(180, 415, "{total_amount}".format(total_amount=booking.total_amount))

        canvas.drawString(430, 660, "{first_name} {last_name}".format(
            first_name=booking.owner.first_name,
            last_name=booking.owner.last_name.upper()
        ))
        canvas.drawString(430, 644, "{phone}".format(phone=booking.owner.phones.all()[0]))
        canvas.drawString(430, 570, "{summary}".format(summary=booking.product.summary))
        return canvas
    