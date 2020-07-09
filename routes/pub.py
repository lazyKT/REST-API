"""
: This is public accessible routes
"""
from flask import Blueprint, render_template, request

from lib.email_helper import send_report


# Initialise BluePrint
pub = Blueprint('pub', __name__)


@pub.route('/')
def index():
    return render_template('index.html')


@pub.route('/about')
def about():
    return render_template('about.html')

# This route is for contact to site admin about help and bug report
@pub.route('/help', methods=['POST'])
def help():
    subject = request.get_json()['subject']
    issue = request.get_json()['issue']
    email = request.get_json()['email']
    try:
        send_report(email, subject, issue)
        return "Success"
    except:
        return "Failed"
