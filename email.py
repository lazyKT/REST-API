"""
: This is a helper class to send/receive emails to/from users. 
: Use cases: Account Created Notification, Password Change, User Feedbacks or Reports
: As flask-mail cannot send message to gmail at default level (due to security issues), 
: I am using built-in functions from SendGrid Twilio
"""
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


""" Email Class """
class EMAIL():

	# __constructor__
	def __init__(self, sender, recipient, subject, html_content):
		self.sender = sender
		self.recipient = recipient
		self.subject = subject
		self.html_content = html_content

	"""
	: This is a helper method to construct email object.
	: Functions from other classes can use this method as per its requirement.
	"""
	def construct_email(self):
		return Mail(
			from_email = self.sender,
			to_emails = self.recipient,
			subject = self.subject,
			html_content = self.html_content
		)
	
	# send message
	def send_message(self):
		pass

message = Mail(
	from_email='kyaw.thitlwin.me@gmail.com',
	to_emails='kyawthit.1996@gmail.com',
	subject='Sending Test Email with SendGrid',
	html_content='<h3>Test Email with SendGrid Twilio</h3>')
try:
	sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
	response = sg.send(message)
	print(response.status_code)
	print(response.body)
	print(response.headers)
except Exception as e:
	print(e.message)
