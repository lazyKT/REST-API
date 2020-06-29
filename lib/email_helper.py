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
	print("Sending Email.....")
	sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
	from_email = Email(sender)
	to_email = To(recipient)
	subject = subject
	# content = Content("text/plain", body)
	mail = Mail(from_email, to_email, subject, html_content=HtmlContent(body))
	response = sg.client.mail.send.post(request_body=mail.get())
	print(response.status_code)
	print(response.body)
	print(response.headers)

# This is a helper function for '/help' route.
# This function allows users to send email about app issues, bugs to the site admin or developer
def send_report(email, title, issue):
	try:
		sender = email
		recipient = os.environ.get('HOST_EMAIL')
		subject = f'[MusiCloud]: {title}'
		send(sender, recipient, subject, body=issue)
	except:
		raise Exception("Error Sending Email")

# This is a helper function to receive an email from user about bugs reports, issues, questions
def receive_report(sender, recipient, subject, body):
	pass