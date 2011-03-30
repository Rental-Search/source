from eloue.rent.models import Booking


def process_booking(uuid):
    booking = Booking.objects.get(uuid=uuid)
    booking.state = Booking.STATE.AUTHORIZED
    booking.send_ask_email()
    booking.save()
    booking.state = Booking.STATE.PENDING
    booking.send_acceptation_email()
    booking.save()
    
    
if __name__=='__main__':
    process_booking("")
    

    