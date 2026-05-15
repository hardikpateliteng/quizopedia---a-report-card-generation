#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stu_test.settings')
django.setup()

from quiz.models import CustomUser

# Get all admins
admins = CustomUser.objects.filter(user_type='admin')
print("=" * 60)
print("ADMINS")
print("=" * 60)
for admin in admins:
    print(f"ID: {admin.id}, Username: {admin.username}, Email: {admin.email}")

print("\n" + "=" * 60)
print("STUDENTS")
print("=" * 60)

# Get all students
students = CustomUser.objects.filter(user_type='student')
for student in students:
    print(f"ID: {student.id}, Username: {student.username}, Email: {student.email}, Enrollment: {student.enrollment_no}")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Total Admins: {admins.count()}")
print(f"Total Students: {students.count()}")
