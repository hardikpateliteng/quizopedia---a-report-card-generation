import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stu_test.settings')
django.setup()

from django.conf import settings

print("\n" + "=" * 70)
print("✓ EMAIL CONFIGURATION TEST")
print("=" * 70)
print(f"\n📧 EMAIL_BACKEND: {settings.EMAIL_BACKEND}")

if "console" in settings.EMAIL_BACKEND:
    print("\n✓ CONSOLE MODE ACTIVE (Development)")
    print("  → Emails will be printed to console/terminal")
    print("  → Perfect for testing!")
else:
    print("\n✓ SMTP MODE ACTIVE (Production)")
    print(f"  → Host: {settings.EMAIL_HOST}")
    print(f"  → Port: {settings.EMAIL_PORT}")
    print(f"  → TLS: {settings.EMAIL_USE_TLS}")
    
print("\n" + "=" * 70)
print("✓ Django is ready! You can now use forgot password feature.")
print("=" * 70 + "\n")

