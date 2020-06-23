"""
: This is a helper function to generate a temporary link for password-reset and user confirmation.
: We can serialize user id inside the url, along with token, and the url will be sent to the users' email address.
: The token includes necessary information like user email and url expiration time.
"""
from itsdangerous import URLSafeTimedSerializer
import os


# !!! : This function generates a token using the given email address(from user)
def generate_link_token(email):
    serializer = URLSafeTimedSerializer(os.environ.get('SECRET_KEY'))
    return serializer.dumps(email, salt=os.environ.get('SECRET_SALT'))

# !!! : This function confirms the token and set the expiration time (default is 3600 seconds).
# !!! : This function validate the token and return the email address until the token has been expired.
def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(os.environ.get('SECRET_KEY'))
    try:
        email = serializer.loads(token, salt=os.environ.get('SECRET_SALT'), max_age=expiration)
    except:
        return False
    return email
