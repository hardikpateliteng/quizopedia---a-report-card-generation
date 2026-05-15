#!/usr/bin/env python
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stu_test.settings')
django.setup()

from django.contrib.auth import get_user_model
from quiz.models import CustomUser, Subject, Quiz, Question, QuizAttempt

User = get_user_model()

print("=" * 70)
print("RESTORING ORIGINAL SEED DATA...")
print("=" * 70)

# Clear all data
QuizAttempt.objects.all().delete()
Question.objects.all().delete()
Quiz.objects.all().delete()
Subject.objects.all().delete()
CustomUser.objects.all().delete()

print("✓ All data cleared successfully!")

print("\n" + "=" * 70)
print("CREATING BASIC ADMINS...")
print("=" * 70)

# Create basic admin
admin_user = CustomUser.objects.create_superuser(
    username='admin',
    email='admin@example.com',
    password='admin',
    user_type='admin'
)
print(f"✓ Admin created - ID: {admin_user.id}, Username: admin, Password: admin")

print("\n" + "=" * 70)
print("CREATING BASIC STUDENTS...")
print("=" * 70)

# Create basic students
students_data = [
    {'username': 'mohit', 'email': 'mohit@gmail.com', 'password': 'password', 'enrollment': None},
    {'username': 'student1', 'email': 'student1@gmail.com', 'password': 'password', 'enrollment': '1'},
    {'username': '220750106019', 'email': 'k@gmail.com', 'password': 'password', 'enrollment': '220750106019'},
    {'username': '100', 'email': 'k2@gmail.com', 'password': 'password', 'enrollment': '100'},
    {'username': 'kunal', 'email': 'kunal@gmail.com', 'password': 'password', 'enrollment': '05'},
]

students = []
for student_data in students_data:
    student = CustomUser.objects.create_user(
        username=student_data['username'],
        email=student_data['email'],
        password=student_data['password'],
        user_type='student',
        enrollment_no=student_data['enrollment']
    )
    students.append(student)
    print(f"✓ Student created - ID: {student.id}, Username: {student_data['username']}, Password: {student_data['password']}")

print("\n" + "=" * 70)
print("CREATING BASIC SUBJECTS...")
print("=" * 70)

# Create basic subjects
subjects_list = ['Mathematics', 'Physics', 'Chemistry', 'Biology', 'Computer Science']
subjects = []
for subject_name in subjects_list:
    subject = Subject.objects.create(name=subject_name, description=f"{subject_name} subject")
    subjects.append(subject)
    print(f"✓ Subject created - {subject_name}")

print("\n" + "=" * 70)
print("CREATING BASIC QUIZZES...")
print("=" * 70)

quizzes = []
now = datetime.now()

quiz_configs = [
    {'title': 'Math Quiz', 'subject': subjects[0], 'is_active': True},
    {'title': 'Physics Quiz', 'subject': subjects[1], 'is_active': True},
    {'title': 'Chemistry Quiz', 'subject': subjects[2], 'is_active': False},
    {'title': 'Biology Quiz', 'subject': subjects[3], 'is_active': True},
    {'title': 'Programming Quiz', 'subject': subjects[4], 'is_active': True},
]

for idx, config in enumerate(quiz_configs, 1):
    quiz = Quiz.objects.create(
        title=config['title'],
        subject=config['subject'],
        description=f"Basic {config['title']}",
        time_limit_minutes=30,
        max_questions=10,
        is_active=config['is_active'],
        start_time=now - timedelta(days=idx),
        end_time=now + timedelta(days=10-idx),
    )
    quizzes.append(quiz)
    status = "ACTIVE" if config['is_active'] else "INACTIVE"
    print(f"✓ Quiz {idx}/5 created - {config['title']} ({status})")

print("\n" + "=" * 70)
print("CREATING BASIC QUESTIONS...")
print("=" * 70)

# Add basic questions to each quiz
for quiz in quizzes:
    for q_num in range(1, 6):  # 5 questions per quiz
        question = Question.objects.create(
            quiz=quiz,
            question_text=f"Question {q_num} for {quiz.title}",
            marks=2,
            subject=quiz.subject,
        )
        # Add basic options
        options = [
            {'text': 'Option A', 'is_correct': q_num == 1},
            {'text': 'Option B', 'is_correct': q_num == 2},
            {'text': 'Option C', 'is_correct': q_num == 3},
            {'text': 'Option D', 'is_correct': q_num == 4},
        ]
        for option in options:
            from quiz.models import Option
            Option.objects.create(
                question=question,
                option_text=option['text'],
                is_correct=option['is_correct']
            )
    print(f"✓ Added 5 questions to: {quiz.title}")

print("\n" + "=" * 70)
print("SEED DATA SUMMARY")
print("=" * 70)

# Summary
print(f"\n✓ Total Admins: {CustomUser.objects.filter(user_type='admin').count()}")
print(f"✓ Total Students: {CustomUser.objects.filter(user_type='student').count()}")
print(f"✓ Total Subjects: {Subject.objects.count()}")
print(f"✓ Total Quizzes: {Quiz.objects.count()} (Active: {Quiz.objects.filter(is_active=True).count()}, Inactive: {Quiz.objects.filter(is_active=False).count()})")
print(f"✓ Total Questions: {Question.objects.count()}")

print("\n" + "=" * 70)
print("ORIGINAL CREDENTIALS")
print("=" * 70)
print("\nADMINS:")
print("  Username: admin        | Password: admin")

print("\nSTUDENTS:")
print("  Username: mohit        | Password: password")
print("  Username: student1     | Password: password")
print("  Username: 220750106019 | Password: password")
print("  Username: 100          | Password: password")
print("  Username: kunal        | Password: password")

print("\n" + "=" * 70)
print("✓ ORIGINAL SEED DATA RESTORED!")
print("=" * 70)
