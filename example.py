
#
# SendGrid Python Example (SendGrid Python Library)
#
# This example shows how to send email through SendGrid
# using Python and the SendGrid Python Library.  For 
# more information on the SendGrid Library, visit:
#
#     https://github.com/sendgrid/sendgrid-python
#
# Before running this example, make sure you have the
# library installed by running the following:
#
#       pip install sendgrid
#       or
#       easy_install sendgrid
#

import sendgrid


# MAKE A SECURE CONNECTION TO SENDGRID
# Fill in the variables below with your SendGrid 
# username and password.
#========================================================#
sg_username = "hugow"
sg_password = "Hl131193"


# CREATE THE SENDGRID MAIL OBJECT
#========================================================#
sg = sendgrid.SendGridClient(sg_username, sg_password)
message = sendgrid.Mail()


# ENTER THE EMAIL INFORMATION
#========================================================#
message.set_from("contact@e-loue.com")
message.set_subject("Subject for %name%")
message.set_text("%%salutation%%,\n\nThis is a test message from SendGrid.    We have sent this to you because you requested a test message be sent from your account.\n\nThis is a link to google.com: http://www.google.com\nThis is a link to apple.com: http://www.apple.com\nThis is a link to sendgrid.com: http://www.sendgrid.com\n\nThank you for reading this test message.\n\nLove,\nYour friends at SendGrid")
message.set_html("<table style=\"border: solid 1px #000; background-color: #666; font-family: verdana, tahoma, sans-serif; color: #fff;\"> <tr> <td> <h2>%%salutation%%,</h2> <p>This is a test message from SendGrid.    We have sent this to you because you requested a test message be sent from your account.</p> <a href=\"http://www.google.com\" target=\"_blank\">This is a link to google.com</a> <p> <a href=\"http://www.apple.com\" target=\"_blank\">This is a link to apple.com</a> <p> <a href=\"http://www.sendgrid.com\" target=\"_blank\">This is a link to sendgrid.com</a> </p> <p>Thank you for reading this test message.</p> Love,<br/> Your friends at SendGrid</p> <p> <img src=\"http://cdn1.sendgrid.com/images/sendgrid-logo.png\" alt=\"SendGrid!\" /> </td> </tr> </table>")



# ADD THE ATTACHMENT
# The first parameter is the name of the file, 
# and the second parameter is the path to the file.
# For the purposes of this demo, the file itself is
# in the same directory as this Python script
#========================================================#
message.add_attachment("sendgrid_logo.jpg", "sendgrid_logo.jpg")



# SMTP API
#========================================================#
# Add the recipients
message.smtpapi.set_tos([
    "hugo@example.none",
    "lucas@example.none",
    "clara@example.none"
])

# Substitutions
subs = {
    "%salutation%": [
        "%mmale_greeting%",
        "%male_greeting%",
        "%female_greeting%"
    ]
    "%name%": [
        "Hugo",
        "lucas",
        "clara"
    ]
}
for tag, values in subs.iteritems():
    for value in values:
        message.add_substitution(tag, value)

# Categories
categories = [
    "New users"
]
for category in categories:
    message.add_category(category)

# Sections
sections = {
    "%%male_greeting%%": "Hello Mr %%name%%"
    "%%female_greeting%%": "Hello Mrs %%name%%"
}
for tag, value in sections.iteritems():
    message.add_section(tag, value)    

# App Filters
filters = {
    "templates": {
        "settings": {
            "enable": "1",
            "template_id": "4deb82f6-c3b3-4caf-8faf-d99cf56d8520"
        }
    }
}
for app, contents in filters.iteritems():
    for setting, value in contents['settings'].iteritems():
        message.add_filter(app, setting, value)




# SEND THE MESSAGE
#========================================================#
status, msg = sg.send(message)

print msg


