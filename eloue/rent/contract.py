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
        canvas.showPage()
        canvas.setFont("Helvetica", 8)

        canvas.drawString(59, 724, u"{first_name} {last_name}".format(
            first_name=booking.owner.first_name,
            last_name=booking.owner.last_name.upper()
        ))

        canvas.drawString(59, 706, u"{phone}".format(phone=booking.owner.phones.all()[0]))
        canvas.drawString(59, 688, u"{address}".format(
            address=booking.owner.default_address or booking.owner.addresses.all()[0])
        )

        if booking.borrower.is_professional:
            canvas.drawString(369, 717, booking.borrower.company_name)

        canvas.drawString(380, 707, u"{first_name} {last_name}".format(
                first_name=booking.borrower.first_name, 
                last_name=booking.borrower.last_name.upper()
            )
        )
        canvas.drawString(364, 698, u"{phone}".format(phone=booking.borrower.phones.all()[0]))
        canvas.drawString(356, 689, u"{address1}".format(
            address1=booking.borrower.default_address or booking.borrower.addresses.all()[0])
        )
        # canvas.drawString(135, 575, "{date_of_birth}, {place_of_birth}".format(
        #         date_of_birth=booking.borrower.date_of_birth.strftime("%d/%m/%Y"),
        #         place_of_birth=booking.borrower.place_of_birth
        #     )
        # )
        canvas.drawString(373, 499, "{masked_number}".format(
            masked_number=booking.borrower.creditcard.masked_number
        ))
        canvas.drawString(352, 483, "{expires1}/{expires2}".format(
            expires1=booking.borrower.creditcard.expires[:2],
            expires2=booking.borrower.creditcard.expires[2:],
        ))


        canvas.drawString(100, 595, u"{summary}".format(summary=booking.product.summary))

        canvas.drawString(170, 561, format(booking.started_at, _(u"d F Y à H\hi.")))
        canvas.drawString(170, 551, format(booking.ended_at, _(u"d F Y à H\hi.")))
        canvas.drawString(122, 542, str(booking.total_amount))
        
        canvas.drawString(382, 619,  str(booking.product.deposit_amount))
        return canvas


class ContractGeneratorCar(ContractGeneratorNormal):
    templates = {
        'fr-fr': local_path("contract/fr_template_car.pdf"),
        'en-uk': local_path("contract/uk_template.pdf"),
    }
    def draw(self, canvas, booking):
        canvas.setFont("Helvetica", 10)
        canvas.drawString(85, 764, u"{first_name} {last_name}".format(
                first_name=booking.borrower.first_name, 
                last_name=booking.borrower.last_name.upper()
            )
        )
        canvas.drawString(72, 752, u"{phone}".format(phone=booking.borrower.phones.all()[0]))
        canvas.drawString(70, 741, u"{address1}".format(address1=booking.borrower.default_address or booking.borrower.addresses.all()[0]))
        canvas.drawString(120, 720, u"{date_of_birth}, {place_of_birth}".format(
                date_of_birth=booking.borrower.date_of_birth.strftime("%d/%m/%Y"),
                place_of_birth=booking.borrower.place_of_birth
            )
        )
        canvas.drawString(115, 710, u"{drivers_license_number}".format(
                drivers_license_number=booking.borrower.drivers_license_number
            )
        )
        canvas.drawString(130, 700, u"{drivers_license_date}".format(
            drivers_license_date=booking.borrower.drivers_license_date.strftime("%d/%m/%Y")
        ))
        canvas.drawString(115, 640, u"{masked_number}".format(
            masked_number=booking.borrower.creditcard.masked_number
        ))
        canvas.drawString(115, 630, u"{expires}".format(
            expires=booking.borrower.creditcard.expires
        ))
        canvas.drawString(170, 535, format(booking.started_at, _(u"d F Y à H\hi.")))
        canvas.drawString(175, 522, format(booking.ended_at, _(u"d F Y à H\hi.")))
        canvas.drawString(168, 490, u"{total_amount}".format(total_amount=booking.total_amount))

        canvas.drawString(430, 760, u"{first_name} {last_name}".format(
            first_name=booking.owner.first_name,
            last_name=booking.owner.last_name.upper()
        ))
        canvas.drawString(430, 744, u"{phone}".format(phone=booking.owner.phones.all()[0]))
        canvas.drawString(430, 710, u"{summary}".format(summary=booking.product.summary))
        canvas.drawString(430, 693, u"{licence_plate}".format(licence_plate=booking.product.carproduct.licence_plate))
        canvas.drawString(430, 680, u"{first_registration_date}".format(first_registration_date=booking.product.carproduct.first_registration_date))
        return canvas
        

class ContractGeneratorRealEstate(ContractGeneratorNormal):
    templates = {
        'fr-fr': local_path("contract/fr_template_realestate.pdf"),
        'en-uk': local_path("contract/uk_template.pdf"),
    }
    def draw(self, canvas, booking):
        # super(ContractGeneratorRealEstate, self).draw(canvas, booking)

        canvas.showPage()
        canvas.setFont("Helvetica", 8)
        canvas.drawString(93, 731, u"{first_name} {last_name}".format(
            first_name=booking.owner.first_name,
            last_name=booking.owner.last_name.upper()
        ))
        canvas.drawString(76, 721, u"{phone}".format(phone=booking.owner.phones.all()[0]))
        
        canvas.drawString(65, 712, u"{address}".format(
            address=booking.owner.default_address or booking.owner.addresses.all()[0])
        )

        if booking.borrower.is_professional:
            canvas.drawString(355, 721, booking.borrower.company_name)

        canvas.drawString(368, 711, u"{first_name} {last_name}".format(
                first_name=booking.borrower.first_name, 
                last_name=booking.borrower.last_name.upper()
            )
        )
        canvas.drawString(352, 702, u"{phone}".format(phone=booking.borrower.phones.all()[0]))
        canvas.drawString(345, 693, u"{address1}".format(
            address1=booking.borrower.default_address or booking.borrower.addresses.all()[0])
        )
        # canvas.drawString(135, 575, "{date_of_birth}, {place_of_birth}".format(
        #         date_of_birth=booking.borrower.date_of_birth.strftime("%d/%m/%Y"),
        #         place_of_birth=booking.borrower.place_of_birth
        #     )
        # )
        canvas.drawString(373, 481, "{masked_number}".format(
            masked_number=booking.borrower.creditcard.masked_number
        ))
        canvas.drawString(352, 464, "{expires1}/{expires2}".format(
            expires1=booking.borrower.creditcard.expires[:2],
            expires2=booking.borrower.creditcard.expires[2:],
        ))


        canvas.drawString(82, 610, u"{summary}".format(summary=booking.product.summary))

        canvas.drawString(152, 573, format(booking.started_at, _(u"d F Y à H\hi.")))
        canvas.drawString(152, 563, format(booking.ended_at, _(u"d F Y à H\hi.")))
        canvas.drawString(102, 553, str(booking.total_amount))
        
        canvas.drawString(382, 610,  str(booking.product.deposit_amount))
        return canvas
