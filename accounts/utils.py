import secrets
import string
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings

def generate_reset_token():
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))

def store_reset_token(email, token, expires_in=600):
    cache_key = f"password_reset:{email}"
    cache.set(cache_key, token, expires_in)

def verify_reset_token(email, token):
    cache_key = f"password_reset:{email}"
    stored_token = cache.get(cache_key)
    return stored_token and stored_token == token

def clear_reset_token(email):
    cache_key = f"password_reset:{email}"
    cache.delete(cache_key)

def send_password_reset_email(email, token):
    subject = 'Password Reset - Bill Station'
    message = f'''
    Hello,
    
    You have requested to reset your password. Please use the following token to reset your password:
    
    Token: {token}
    
    This token will expire in 10 minutes.
    
    If you did not request this password reset, please ignore this email.
    
    Best regards,
    Bill Station Team
    '''
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False