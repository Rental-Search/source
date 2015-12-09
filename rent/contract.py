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
        'fr-FR': local_path("contract/contrat_sans_assurance.pdf"),
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
        canvas.drawString(144, 721, u"{email}".format(email=(booking.owner.email)))

        canvas.drawString(80, 702, u"{address}".format(
            address=booking.owner.default_address or first_or_empty(booking.owner.addresses.all()))
        )

        if booking.borrower.is_professional:
            canvas.drawString(383, 743, booking.borrower.company_name)

        canvas.drawString(383, 743, u"{first_name} {last_name}".format(
                first_name=booking.borrower.first_name, 
                last_name=booking.borrower.last_name.upper()
            )
        )
        canvas.drawString(363, 732, u"{phone}".format(phone=first_or_empty(booking.borrower.phones.all())))
        canvas.drawString(378, 722, u"{email}".format(email=(booking.borrower.email)))
        canvas.drawString(314, 702, u"{address1}".format(
            address1=booking.borrower.default_address or first_or_empty(booking.borrower.addresses.all()))
        )

        canvas.drawString(379, 417, "{masked_number}".format(
            masked_number=booking.payment.creditcard.masked_number
        ))
        canvas.drawString(360, 391, "{expires1}/{expires2}".format(
            expires1=booking.payment.creditcard.expires[:2],
            expires2=booking.payment.creditcard.expires[2:],
        ))

        canvas.drawString(80, 610, u"{summary}".format(summary=smart_str(booking.product.summary)))

        booking_total_amount = "%s %s" % (str(booking.total_amount), u"\u20AC")
        booking_deposit_amount = "%s %s" % (str(booking.product.deposit_amount), u"\u20AC")
        
        canvas.drawString(81, 589, format(booking.started_at, _(u"d F Y à H\hi.")))
        canvas.drawString(81, 568, format(booking.ended_at, _(u"d F Y à H\hi.")))
        canvas.drawString(156, 557, u"{booking_total_amount}".format(booking_total_amount=booking_total_amount))
        canvas.drawString(388, 621, u"{booking_total_amount}".format(booking_total_amount=booking_total_amount))
        
        canvas.drawString(156, 487,  u"{booking_deposit_amount}".format(booking_deposit_amount=booking_deposit_amount))
        return canvas


class ContractGeneratorNormal(ContractGenerator):
    if settings.SITE_ID == 15:
        templates = {
            'fr-FR': local_path("contract/fr_template_normal_dressbooking.pdf")
        }
    else:
        templates = {
            'fr-FR': local_path("contract/fr_template_normal.pdf")
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
        canvas.drawString(137, 722, u"{email}".format(email=(booking.owner.email)))
        canvas.drawString(81, 702, u"{address}".format(
            address=booking.owner.default_address or first_or_empty(booking.owner.addresses.all()))
        )

        
        if booking.borrower.is_professional:
            canvas.drawString(383, 743, booking.borrower.company_name)

        canvas.drawString(383, 743, u"{first_name} {last_name}".format(
                first_name=booking.borrower.first_name, 
                last_name=booking.borrower.last_name.upper()
            )
        )
        canvas.drawString(363, 732, u"{phone}".format(phone=first_or_empty(booking.borrower.phones.all())))
        canvas.drawString(373, 722, u"{email}".format(email=(booking.borrower.email)))
        canvas.drawString(315, 702, u"{address}".format(
            address=booking.borrower.default_address or first_or_empty(booking.borrower.addresses.all()))
        )
        

        canvas.drawString(380, 407, "{masked_number}".format(
            masked_number=booking.payment.creditcard.masked_number
        ))
        canvas.drawString(355, 389, "{expires1}/{expires2}".format(
            expires1=booking.payment.creditcard.expires[:2],
            expires2=booking.payment.creditcard.expires[2:],
        ))

        canvas.drawString(80, 610, u"{summary}".format(summary=booking.product.summary))

        booking_total_amount = "%s %s" % (str(booking.total_amount), u"\u20AC")
        booking_deposit_amount = "%s %s" % (str(booking.product.deposit_amount), u"\u20AC")

        canvas.drawString(81, 589, format(booking.started_at, _(u"d F Y à H\hi.")))
        canvas.drawString(81, 568, format(booking.ended_at, _(u"d F Y à H\hi.")))
        canvas.drawString(389, 621, u"{booking_total_amount}".format(booking_total_amount=booking_total_amount))
        canvas.drawString(156, 557 , u"{booking_total_amount}".format(booking_total_amount=booking_total_amount))
        
        canvas.drawString(156, 491, u"{booking_deposit_amount}".format(booking_deposit_amount=booking_deposit_amount))


        return canvas


class ContractGeneratorCar(ContractGenerator):
    templates = {
        'fr-FR': local_path("contract/contrat_voiture.pdf"),
        'en-uk': local_path("contract/uk_template.pdf"),
    }
    def draw(self, canvas, booking):
        canvas.showPage()
        canvas.setFont("Helvetica", 8)
        canvas.drawString(147, 756, u"{first_name} {last_name}".format(
            first_name=booking.borrower.first_name.upper(),
            last_name=booking.borrower.last_name.upper()
        ))

        canvas.drawString(127, 745, u"{phone}".format(phone=first_or_empty(booking.borrower.phones.all())))
        canvas.drawString(145, 734, u"{email}".format(email=(booking.borrower.email)))
        canvas.drawString(78, 715, u"{address}".format(
            address=booking.borrower.default_address or first_or_empty(booking.borrower.addresses.all()))
        )
        canvas.drawString(180, 695, "{date_of_birth}, {place_of_birth}".format(
                date_of_birth=booking.borrower.date_of_birth.strftime("%d/%m/%Y"),
                place_of_birth=booking.borrower.place_of_birth
            )
        )
        canvas.drawString(171, 685, u"{drivers_license_number}".format(
                drivers_license_number=booking.borrower.drivers_license_number
            )
        )
        canvas.drawString(190, 675, u"{drivers_license_date}".format(
            drivers_license_date=booking.borrower.drivers_license_date.strftime("%d/%m/%y")
        ))



        canvas.drawString(381, 756, u"{first_name} {last_name}".format(
                first_name=booking.owner.first_name, 
                last_name=booking.owner.last_name.upper()))
        canvas.drawString(361, 745, u"{phone}".format(phone=first_or_empty(booking.owner.phones.all())))
        canvas.drawString(377, 734, u"{email}".format(email=(booking.owner.email)))
        canvas.drawString(311, 713, u"{address}".format(
            address=booking.owner.default_address or first_or_empty(booking.owner.addresses.all()))
        )
        

        canvas.drawString(388, 667, u"{summary}".format(summary=smart_str(booking.product.summary)))



        canvas.drawString(382, 657, u"{licence_plate}".format(licence_plate=booking.product.carproduct.licence_plate))
        canvas.drawString(428, 646, u"{first_registration_date}".format(first_registration_date=booking.product.carproduct.first_registration_date))



        canvas.drawString(205, 602, format(booking.started_at, _(u"d F Y à H\hi.")))
        canvas.drawString(205, 591, format(booking.ended_at, _(u"d F Y à H\hi.")))

        
        km_included = "%s %s" % (booking.product.carproduct.km_included or 0, "km")
        delta = booking.ended_at - booking.started_at
        total_km_included = "%s %s" % (round(delta.days + delta.seconds/60/60/24., 2)*booking.product.carproduct.km_included or 0, "km")
        costs_per_km = "%s %s" % (booking.product.carproduct.costs_per_km or 0, u"\u20AC")
        booking_total_amount = "%s %s" % (str(booking.total_amount), u"\u20AC")

        canvas.drawString(205, 581, u"{km_included}".format(km_included=km_included))
        canvas.drawString(198, 571, u"{total_km_included}".format(total_km_included=total_km_included))
        canvas.drawString(203, 560, u"{costs_per_km}".format(costs_per_km=costs_per_km))
        canvas.drawString(153, 549, u"{booking_total_amount}".format(booking_total_amount=booking_total_amount))

        canvas.drawString(149, 529, "{masked_number}".format(
            masked_number=booking.payment.creditcard.masked_number
        ))
        canvas.drawString(124, 499, "{expires1}/{expires2}".format(
            expires1=booking.payment.creditcard.expires[:2],
            expires2=booking.payment.creditcard.expires[2:],
        ))

        return canvas
        

class ContractGeneratorRealEstate(ContractGenerator):
    templates = {
        'fr-FR': local_path("contract/contrat_location_saisonniere.pdf"),
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
        canvas.drawString(137, 722, u"{email}".format(email=(booking.owner.email)))
        canvas.drawString(81, 701, u"{address}".format(
            address=booking.owner.default_address or first_or_empty(booking.owner.addresses.all()))
        )

        if booking.borrower.is_professional:
            canvas.drawString(383, 743, booking.borrower.company_name)

        canvas.drawString(383, 743, u"{first_name} {last_name}".format(
                first_name=booking.borrower.first_name, 
                last_name=booking.borrower.last_name.upper()
            )
        )
        canvas.drawString(362, 732, u"{phone}".format(phone=first_or_empty(booking.borrower.phones.all())))
        canvas.drawString(372, 722, u"{email}".format(email=(booking.borrower.email)))
        canvas.drawString(315, 701, u"{address}".format(
            address=booking.borrower.default_address or first_or_empty(booking.borrower.addresses.all()))
        )

        canvas.drawString(379, 401, "{masked_number}".format(
            masked_number=booking.payment.creditcard.masked_number
        ))
        canvas.drawString(355, 382, "{expires1}/{expires2}".format(
            expires1=booking.payment.creditcard.expires[:2],
            expires2=booking.payment.creditcard.expires[2:],
        ))
       
        canvas.drawString(80, 608, u"{summary}".format(summary=booking.product.summary))

        booking_total_amount = "%s %s" % (str(booking.total_amount), u"\u20AC")
        booking_deposit_amount = "%s %s" % (str(booking.product.deposit_amount), u"\u20AC")

        canvas.drawString(81, 587, format(booking.started_at, _(u"d F Y à H\hi.")))
        canvas.drawString(81, 566, format(booking.ended_at, _(u"d F Y à H\hi.")))
        canvas.drawString(389, 616, u"{booking_total_amount}".format(booking_total_amount=booking_total_amount))
        canvas.drawString(156, 554 , u"{booking_total_amount}".format(booking_total_amount=booking_total_amount))
        
        canvas.drawString(156, 491, u"{booking_deposit_amount}".format(booking_deposit_amount=booking_deposit_amount))
        return canvas
