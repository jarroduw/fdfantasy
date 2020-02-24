from fdfantasy.settings import *

ROOT_URL = 'fdfantasy.com'

STATIC_ROOT = '/var/www/fdfantasy/static/'
MEDIA_ROOT = '/var/www/fdfantasy/media/'

with open('__sensitive_emailPw.txt') as fi:
    emailPw = fi.read().strip()

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'email-smtp.us-west-2.amazonaws.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'AKIA4PXL5JUP7JKC5TND'
EMAIL_HOST_PASSWORD = emailPw
DEFAULT_FROM_EMAIL = 'admin@fdfantasy.com'
SERVER_EMAIL = 'admin@fdfantasy.com'
