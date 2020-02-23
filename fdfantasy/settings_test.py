from fdfantasy.settings import *

STATIC_ROOT = '/var/www/fdfantasy/static/'
MEDIA_ROOT = '/var/www/fdfantasy/media/'

with open('__sensitive_emailPw.txt') as fi:
    emailPw = fi.read().strip()

EMAIl_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'email-smtp.us-east-1.amazonaws.com'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'AKIA4PXL5JUPU5SMBG6B'
EMAIL_HOST_PASSWORD = emailPw
DEFAULT_FROM_EMAIL = 'admin@fdfantasy.com'
