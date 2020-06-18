"""
: This is a helper class to send/receive emails to/from users. 
: Use cases: Account Created Notification, Password Change, User Feedbacks or Reports
: As flask-mail cannot send message to gmail at default level (due to security issues), 
: I am using built-in functions from SendGrid Twilio
"""


# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import sendgrid
import os
from sendgrid.helpers.mail import *


def send(sender, recipient, subject, body):
	sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
	from_email = Email(sender)
	to_email = To(recipient)
	subject = subject
	content = Content("text/plain", body)
	mail = Mail(from_email, to_email, subject, content)
	response = sg.client.mail.send.post(request_body=mail.get())
	print(response.status_code)
	print(response.body)
	print(response.headers)
