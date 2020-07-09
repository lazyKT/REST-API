"""
: The all routes  below are associated with User's email address, like..
: User Confirmation, Password reset, de/activate accounts
"""
from flask import Blueprint, render_template, request
from flask_jwt_extended import jwt_required

from models.users import UserModel

from resources.users import password_forget, password_reset

from lib.link_token import confirm_token, generate_link_token

#Blueprint iniitialization
mail = Blueprint('mail', __name__)


"""
: This is a route for the user confirmation.
: This route is sent to user's email address after succesful registeration.
: Users must click this route in their email inbox to activate their account.
: InActive users cannot be validated and cannot access the mail.
"""
@mail.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        return "The Confirmation Link has been invalid or expired."
    if not email:
        return "The Confirmation Link has been expired.\nIf you account has not confirmed yet, try to log in to get confirmation link"
    user = UserModel.find_by_email(email)
    if not user:
        return "User Not Found"
    if user.status == "Active":
        return "Your account already confirmed and active."
    else:
        UserModel.activate_account(user.id)
        return render_template('activate.html')


"""
: This route is for the activation of the account for the deactivated users.
: The deactivated users can refer to this route to re-activate their account with their email addresses.
"""
@mail.route('/re-activate', methods=['POST'])
def activate_account():
    user = UserModel.find_by_email(request.get_json()['email'])
    if not user:
        return {'msg': "User account related to this email address, is not found."}, 404
    token = generate_link_token(user.email)
    UserModel.send_confirmation_email(token, user.email, user.username)
    return {'msg': "An Activation Link has been sent to your email Address."}, 200


"""
: This is a route to deactivate the account.
: Users can deactivate the account by sending this route.
"""
@mail.route('/deactivate/<username>')
@jwt_required
def deactivate_account(username):
    user = UserModel.find_by_username(username)
    UserModel.deactivate_account(user.id)
    return {'msg': "Account Deactivated!"}, 200


"""
: This route is to request the password reset link when users forgot their password at login.
"""
@mail.route('/forget-password', methods=['POST'])
def forget_password():
    try:
        email = request.get_json()['email']
        res = password_forget(email)
        return res
    except:
        return {'msg': "Key-Error 'email'"}, 400


"""
: Password Reset Link.
: This route is the password reset link for users who forgot their passwords on Login Page
: Users click 'Forgot Password?' link and the route link will be sent to their emails.
"""
@mail.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = confirm_token(token, expiration=600) # ! expired in 10 minutes
    except:
        return "The reset-password link is invalid or expired."
    if not email:
        return "The reset-password link is expired. Try to request new one."
    user = UserModel.find_by_email(email)
    if user and request.method == 'GET':
        return render_template('reset_pwd.html', username = user.username)
    if request.form['reset'] == 'Reset':
        if request.form['password'] == request.form['confirm_pwd']:
            password = request.form['password']
            return password_reset(user.id, password)
        else: # If passwords doesn't match. Alert User
            return render_template('reset_pwd.html', username = user.username)
