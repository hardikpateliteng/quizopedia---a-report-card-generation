#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stu_test.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Create superuser
username = 'admin2'
password = 'admin2'
email = 'admin2@example.com'

try:
    if User.objects.filter(username=username).exists():
        print(f"User '{username}' already exists!")
    else:
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            user_type='admin'
        )
        print(f"✓ Superuser '{username}' created successfully!")
        print(f"  ID: {user.id}")
        print(f"  Username: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  User Type: {user.user_type}")
except Exception as e:
    print(f"✗ Error creating superuser: {e}")
