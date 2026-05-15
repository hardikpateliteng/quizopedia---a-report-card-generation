import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stu_test.settings')
django.setup()
from django.core.mail import send_mail
from django.conf import settings
print('backend', settings.EMAIL_BACKEND)
print('host', getattr(settings,'EMAIL_HOST','<unset>'))
print('user', getattr(settings,'EMAIL_HOST_USER','<unset>'))
try:
    r = send_mail('Test Email OTP', 'Your test OTP is 123456', settings.EMAIL_HOST_USER, ['rathodnikhil1107@gmail.com'], fail_silently=False)
    print('send_mail result', r)
except Exception as e:
    print('send_mail exception', type(e).__name__, e)
