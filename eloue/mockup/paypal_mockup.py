# -*- coding: utf-8 -*-

def fake_verify_paypal_account(email, first_name, last_name):
    print ">>>>>>>> fake method called  >>>>>>>>>"
    if email == "invalid@e-loue.com":
        return "INVALID"
    elif email == "verified@e-loue.com":
        return "VERIFIED"
    elif email == "unverified@e-loue.com":
        return "UNVERIFIED"
    else:
        return None