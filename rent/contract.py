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
from django.utils.encoding import force_unicode, smart_str
from django.utils.translation import ugettext as _

from rent.utils import spellout

local_path = lambda path: os.path.join(os.path.dirname(__file__), path)

def first_or_empty(alist):
    if alist:
        return alist[0]
    return ''

class ContractGenerator(object):
    templates = {
        'fr-fr': local_path("contract/new_contrat_sans_assurance_fr.pdf"),
        'en-uk': local_path("contract/uk_template.pdf"),
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

        canvas.drawString(148, 743, u"{first_name} {last_name}".format(
            first_name=booking.owner.first_name,
            last_name=booking.owner.last_name.upper()
        ))

        canvas.drawString(128, 733, u"{phone}".format(phone=first_or_empty(booking.owner.phones.all())))
        canvas.drawString(80, 702, u"{address}".format(
            address=booking.owner.default_address or first_or_empty(booking.owner.addresses.all()))
        )

        if booking.borrower.is_professional:
            canvas.drawString(369, 717, booking.borrower.company_name)

        canvas.drawString(383, 743, u"{first_name} {last_name}".format(
                first_name=booking.borrower.first_name, 
                last_name=booking.borrower.last_name.upper()
            )
        )
        canvas.drawString(333, 733, u"{phone}".format(phone=first_or_empty(booking.borrower.phones.all())))
        canvas.drawString(315, 702, u"{address1}".format(
            address1=booking.borrower.default_address or first_or_empty(booking.borrower.addresses.all()))
        )

        canvas.drawString(379, 417, "{masked_number}".format(
            masked_number=booking.payment.creditcard.masked_number
        ))
        canvas.drawString(363, 391, "{expires1}/{expires2}".format(
            expires1=booking.payment.creditcard.expires[:2],
            expires2=booking.payment.creditcard.expires[2:],
        ))

        canvas.drawString(127, 621, u"{summary}".format(summary=smart_str(booking.product.summary)))

        canvas.drawString(81, 594, format(booking.started_at, _(u"d F Y à H\hi.")))
        canvas.drawString(81, 573, format(booking.ended_at, _(u"d F Y à H\hi.")))
        canvas.drawString(152, 553, str(booking.total_amount))
        canvas.drawString(388, 621, str(booking.total_amount))
        
        canvas.drawString(157, 487,  str(booking.product.deposit_amount))
        return canvas


class ContractGeneratorNormal(ContractGenerator):
    templates = {
        'fr-fr': local_path("contract/fr_template_normal.pdf")
    }
    
    def draw(self, canvas, booking):
        """Draw stuff in the carbon"""
        canvas.showPage()
        canvas.setFont("Helvetica", 8)

        canvas.drawString(148, 743, u"{first_name} {last_name}".format(
            first_name=booking.owner.first_name,
            last_name=booking.owner.last_name.upper()
        ))

        canvas.drawString(128, 732, u"{phone}".format(phone=first_or_empty(booking.owner.phones.all())))
        canvas.drawString(81, 712, u"{address}".format(
            address=booking.owner.default_address or first_or_empty(booking.owner.addresses.all()))
        )

        if booking.borrower.is_professional:
            canvas.drawString(369, 717, booking.borrower.company_name)

        canvas.drawString(383, 743, u"{first_name} {last_name}".format(
                first_name=booking.borrower.first_name, 
                last_name=booking.borrower.last_name.upper()
            )
        )
        canvas.drawString(363, 732, u"{phone}".format(phone=first_or_empty(booking.borrower.phones.all())))
        canvas.drawString(315, 712, u"{address1}".format(
            address1=booking.borrower.default_address or first_or_empty(booking.borrower.addresses.all()))
        )

        canvas.drawString(378, 427, "{masked_number}".format(
            masked_number=booking.payment.creditcard.masked_number
        ))
        canvas.drawString(354, 408, "{expires1}/{expires2}".format(
            expires1=booking.payment.creditcard.expires[:2],
            expires2=booking.payment.creditcard.expires[2:],
        ))


        canvas.drawString(127, 621, u"{summary}".format(summary=booking.product.summary))

        canvas.drawString(81, 579, format(booking.started_at, _(u"d F Y à H\hi.")))
        canvas.drawString(81, 558, format(booking.ended_at, _(u"d F Y à H\hi.")))
        canvas.drawString(389, 610, str(booking.total_amount))
        
        canvas.drawString(157, 510,  str(booking.product.deposit_amount))

        canvas.showPage()
        canvas.setFont("Helvetica", 8)

        #locataire
        canvas.drawString(130, 721,  u"{first_name} {last_name}".format(
                first_name=booking.borrower.first_name.upper(), 
                last_name=booking.borrower.last_name.upper()
            )
        )

        borrower_address = booking.borrower.default_address or first_or_empty(booking.borrower.addresses.all())

        canvas.drawString(100, 706,  u"{address1}".format(
            address1=borrower_address.address1 if borrower_address else '')
        )

        canvas.drawString(113, 690, u"{zipcode} {city}".format(
                zipcode=borrower_address.zipcode if borrower_address else '',
                city=borrower_address.city if borrower_address else '',
            )
        )

        canvas.drawString(153, 674, u"{deposit_amount} euros".format(
            deposit_amount=booking.product.deposit_amount)
        )

        canvas.drawString(131, 658, smart_str(booking.product.summary))

        canvas.drawString(65, 628, smart_str(booking.product.summary))


        #propriétaire
        canvas.drawString(353, 721, u"{first_name} {last_name}".format(
                first_name=booking.owner.first_name.upper(), 
                last_name=booking.owner.last_name.upper()
            )

        )

        owner_address = booking.owner.default_address or first_or_empty(booking.owner.addresses.all())

        canvas.drawString(323, 706,  u"{address1}".format(
            address1=owner_address.address1 if owner_address else ''))

        canvas.drawString(336, 690, u"{zipcode} {city}".format(
                zipcode=owner_address.zipcode if owner_address else '',
                city=owner_address.city if owner_address else '',
            )
        )

        canvas.drawString(338, 626, format(booking.started_at, _(u"d F Y à H\hi.")))

        canvas.drawString(336, 611, format(booking.ended_at, _(u"d F Y à H\hi.")))

        return canvas



class ContractGeneratorCar(ContractGenerator):
    templates = {
        'fr-fr': local_path("contract/fr_template_car.pdf"),
        'en-uk': local_path("contract/uk_template.pdf"),
    }
    def draw(self, canvas, booking):
        canvas.showPage()
        canvas.setFont("Helvetica", 8)
        canvas.drawString(144, 764, u"{first_name} {last_name}".format(
            first_name=booking.borrower.first_name.upper(),
            last_name=booking.borrower.last_name.upper()
        ))

        canvas.drawString(126, 754, u"{phone}".format(phone=first_or_empty(booking.borrower.phones.all())))
        canvas.drawString(81, 734, u"{address}".format(
            address=booking.borrower.default_address or first_or_empty(booking.borrower.addresses.all()))
        )
        canvas.drawString(180, 712, "{date_of_birth}, {place_of_birth}".format(
                date_of_birth=booking.borrower.date_of_birth.strftime("%d/%m/%Y"),
                place_of_birth=booking.borrower.place_of_birth
            )
        )
        canvas.drawString(172, 701, u"{drivers_license_number}".format(
                drivers_license_number=booking.borrower.drivers_license_number
            )
        )
        canvas.drawString(192, 691, u"{drivers_license_date}".format(
            drivers_license_date=booking.borrower.drivers_license_date.strftime("%d/%m/%y")
        ))



        canvas.drawString(379, 764, u"{first_name} {last_name}".format(
                first_name=booking.owner.first_name, 
                last_name=booking.owner.last_name.upper()
            )
        )
        canvas.drawString(361, 754, u"{phone}".format(phone=first_or_empty(booking.owner.phones.all())))

        canvas.drawString(388, 722, u"{summary}".format(summary=smart_str(booking.product.summary)))



        canvas.drawString(382, 712, u"{licence_plate}".format(licence_plate=booking.product.carproduct.licence_plate))
        canvas.drawString(428, 701, u"{first_registration_date}".format(first_registration_date=booking.product.carproduct.first_registration_date))



        canvas.drawString(205, 612, format(booking.started_at, _(u"d F Y à H\hi.")))
        canvas.drawString(205, 601, format(booking.ended_at, _(u"d F Y à H\hi.")))

        delta = booking.ended_at - booking.started_at
        total_km_included = round(delta.days + delta.seconds/60/60/24., 2)*booking.product.carproduct.km_included
        canvas.drawString(198, 591, u"{km_included}".format(km_included=total_km_included or 0))
        canvas.drawString(203, 580, u"{costs_per_km}".format(costs_per_km=booking.product.carproduct.costs_per_km or 0))
        canvas.drawString(154, 569, str(booking.total_amount))

        canvas.drawString(148, 550, "{masked_number}".format(
            masked_number=booking.payment.creditcard.masked_number
        ))
        canvas.drawString(122, 519, "{expires1}/{expires2}".format(
            expires1=booking.payment.creditcard.expires[:2],
            expires2=booking.payment.creditcard.expires[2:],
        ))

        

        return canvas
        

class ContractGeneratorRealEstate(ContractGenerator):
    templates = {
        'fr-fr': local_path("contract/fr_template_realestate.pdf"),
        'en-uk': local_path("contract/uk_template.pdf"),
    }
    def draw(self, canvas, booking):
        # super(ContractGeneratorRealEstate, self).draw(canvas, booking)

        canvas.showPage()
        canvas.setFont("Helvetica", 8)
        canvas.drawString(148, 743, u"{first_name} {last_name}".format(
            first_name=booking.owner.first_name,
            last_name=booking.owner.last_name.upper()
        ))
        canvas.drawString(128, 732, u"{phone}".format(phone=first_or_empty(booking.owner.phones.all())))
        
        canvas.drawString(81, 712, u"{address}".format(
            address=booking.owner.default_address or first_or_empty(booking.owner.addresses.all()))
        )

        if booking.borrower.is_professional:
            canvas.drawString(355, 721, booking.borrower.company_name)

        canvas.drawString(383, 743, u"{first_name} {last_name}".format(
                first_name=booking.borrower.first_name, 
                last_name=booking.borrower.last_name.upper()
            )
        )
        canvas.drawString(363, 732, u"{phone}".format(phone=first_or_empty(booking.borrower.phones.all())))
        canvas.drawString(315, 712, u"{address1}".format(
            address1=booking.borrower.default_address or first_or_empty(booking.borrower.addresses.all()))
        )

        canvas.drawString(378, 427, "{masked_number}".format(
            masked_number=booking.payment.creditcard.masked_number
        ))
        canvas.drawString(354, 408, "{expires1}/{expires2}".format(
            expires1=booking.payment.creditcard.expires[:2],
            expires2=booking.payment.creditcard.expires[2:],
        ))
        
        canvas.drawString(127, 628, u"{summary}".format(summary=smart_str(booking.product.summary)))

        canvas.drawString(81, 585, format(booking.started_at, _(u"d F Y à H\hi.")))
        canvas.drawString(81, 564, format(booking.ended_at, _(u"d F Y à H\hi.")))
        canvas.drawString(389, 615, str(booking.total_amount))
        
        canvas.drawString(157, 510,  str(booking.product.deposit_amount))
        return canvas
