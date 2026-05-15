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
print("CLEARING ALL SEED DATA...")
print("=" * 70)

# Delete all data
QuizAttempt.objects.all().delete()
Question.objects.all().delete()
Quiz.objects.all().delete()
Subject.objects.all().delete()
CustomUser.objects.all().delete()

print("✓ All data cleared successfully!")

print("\n" + "=" * 70)
print("CREATING ADMIN USERS...")
print("=" * 70)

# Create admin user
admin_user = CustomUser.objects.create_superuser(
    username='admin',
    email='admin@example.com',
    password='admin',
    user_type='admin'
)
print(f"✓ Admin created - ID: {admin_user.id}, Username: admin, Password: admin")

# Create admin2 user
admin2_user = CustomUser.objects.create_superuser(
    username='admin2',
    email='admin2@example.com',
    password='admin2',
    user_type='admin'
)
print(f"✓ Admin created - ID: {admin2_user.id}, Username: admin2, Password: admin2")

print("\n" + "=" * 70)
print("CREATING STUDENT USERS...")
print("=" * 70)

# Create student - Hardik
hardik_student = CustomUser.objects.create_user(
    username='hardik',
    email='hardik@example.com',
    password='12',
    user_type='student',
    enrollment_no='2202031000179',
    first_name='Hardik',
    last_name='Patel'
)
print(f"✓ Student created - ID: {hardik_student.id}, Username: hardik, Password: 12")

# Create more students
students_data = [
    {'username': 'student1', 'email': 'student1@example.com', 'password': 'pass1', 'enrollment': '101', 'name': 'Rahul Kumar'},
    {'username': 'student2', 'email': 'student2@example.com', 'password': 'pass2', 'enrollment': '102', 'name': 'Priya Singh'},
    {'username': 'student3', 'email': 'student3@example.com', 'password': 'pass3', 'enrollment': '103', 'name': 'Amit Sharma'},
    {'username': 'student4', 'email': 'student4@example.com', 'password': 'pass4', 'enrollment': '104', 'name': 'Neha Gupta'},
    {'username': 'student5', 'email': 'student5@example.com', 'password': 'pass5', 'enrollment': '105', 'name': 'Vikram Patel'},
]

students = [hardik_student]
for student_data in students_data:
    student = CustomUser.objects.create_user(
        username=student_data['username'],
        email=student_data['email'],
        password=student_data['password'],
        user_type='student',
        enrollment_no=student_data['enrollment'],
        first_name=student_data['name'].split()[0],
        last_name=' '.join(student_data['name'].split()[1:])
    )
    students.append(student)
    print(f"✓ Student created - ID: {student.id}, Username: {student_data['username']}, Password: {student_data['password']}")

print("\n" + "=" * 70)
print("CREATING SUBJECTS...")
print("=" * 70)

# Create subjects
subjects_list = [
    'Mathematics',
    'Physics',
    'Chemistry',
    'Biology',
    'Computer Science',
]

subjects = []
for subject_name in subjects_list:
    subject = Subject.objects.create(name=subject_name, description=f"{subject_name} subject")
    subjects.append(subject)
    print(f"✓ Subject created - {subject_name}")

print("\n" + "=" * 70)
print("CREATING 10 QUIZZES...")
print("=" * 70)

quizzes = []
now = datetime.now()

quiz_configs = [
    {'title': 'Math Basics Quiz', 'subject': subjects[0], 'is_active': True, 'time_limit': 30},
    {'title': 'Physics Chapter 1', 'subject': subjects[1], 'is_active': True, 'time_limit': 45},
    {'title': 'Chemistry Formulas', 'subject': subjects[2], 'is_active': False, 'time_limit': 30},
    {'title': 'Biology Basics', 'subject': subjects[3], 'is_active': True, 'time_limit': 40},
    {'title': 'Python Programming', 'subject': subjects[4], 'is_active': True, 'time_limit': 60},
    {'title': 'Algebra Advanced', 'subject': subjects[0], 'is_active': False, 'time_limit': 50},
    {'title': 'Quantum Physics', 'subject': subjects[1], 'is_active': True, 'time_limit': 45},
    {'title': 'Organic Chemistry', 'subject': subjects[2], 'is_active': True, 'time_limit': 35},
    {'title': 'Human Anatomy', 'subject': subjects[3], 'is_active': False, 'time_limit': 40},
    {'title': 'Data Structures', 'subject': subjects[4], 'is_active': True, 'time_limit': 55},
]

for idx, config in enumerate(quiz_configs, 1):
    quiz = Quiz.objects.create(
        title=config['title'],
        subject=config['subject'],
        description=f"Quiz for {config['title']}",
        time_limit_minutes=config['time_limit'],
        max_questions=10,
        is_active=config['is_active'],
        start_time=now - timedelta(days=idx),
        end_time=now + timedelta(days=10-idx),
    )
    quizzes.append(quiz)
    status = "ACTIVE" if config['is_active'] else "INACTIVE"
    print(f"✓ Quiz {idx}/10 created - {config['title']} ({status})")

print("\n" + "=" * 70)
print("CREATING SAMPLE QUESTIONS FOR QUIZZES...")
print("=" * 70)

# Add sample questions to each quiz
for quiz in quizzes:
    for q_num in range(1, 6):  # 5 questions per quiz
        question = Question.objects.create(
            quiz=quiz,
            question_text=f"Question {q_num} for {quiz.title}",
            marks=2,
            subject=quiz.subject,
        )
        # Add options
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
print("CREATING QUIZ ATTEMPTS (STUDENTS TAKING EXAMS)...")
print("=" * 70)

# Make some students attempt some quizzes
quiz_attempt_configs = [
    {'student': students[0], 'quiz': quizzes[0], 'score': 18, 'is_completed': True},  # Hardik - Math Basics
    {'student': students[0], 'quiz': quizzes[1], 'score': 35, 'is_completed': True},  # Hardik - Physics
    {'student': students[1], 'quiz': quizzes[0], 'score': 16, 'is_completed': True},  # Student1 - Math
    {'student': students[1], 'quiz': quizzes[4], 'score': 40, 'is_completed': True},  # Student1 - Python
    {'student': students[2], 'quiz': quizzes[1], 'score': 30, 'is_completed': True},  # Student2 - Physics
    {'student': students[2], 'quiz': quizzes[3], 'score': 20, 'is_completed': True},  # Student2 - Biology
    {'student': students[3], 'quiz': quizzes[4], 'score': 45, 'is_completed': True},  # Student3 - Python
    {'student': students[4], 'quiz': quizzes[0], 'score': 12, 'is_completed': True},  # Student4 - Math
]

for attempt_config in quiz_attempt_configs:
    attempt = QuizAttempt.objects.create(
        student=attempt_config['student'],
        quiz=attempt_config['quiz'],
        score=attempt_config['score'],
        is_completed=attempt_config['is_completed'],
        time_taken_seconds=attempt_config['quiz'].time_limit_minutes * 60
    )
    print(f"✓ Quiz Attempt: {attempt_config['student'].username} attempted {attempt_config['quiz'].title} - Score: {attempt_config['score']}")

print("\n" + "=" * 70)
print("SEED DATA SUMMARY")
print("=" * 70)

# Summary
print(f"\n✓ Total Admins: {CustomUser.objects.filter(user_type='admin').count()}")
print(f"✓ Total Students: {CustomUser.objects.filter(user_type='student').count()}")
print(f"✓ Total Subjects: {Subject.objects.count()}")
print(f"✓ Total Quizzes: {Quiz.objects.count()} (Active: {Quiz.objects.filter(is_active=True).count()}, Inactive: {Quiz.objects.filter(is_active=False).count()})")
print(f"✓ Total Questions: {Question.objects.count()}")
print(f"✓ Total Quiz Attempts: {QuizAttempt.objects.count()}")

print("\n" + "=" * 70)
print("ADMIN & STUDENT CREDENTIALS")
print("=" * 70)
print("\nADMINS:")
print("  Username: admin        | Password: admin")
print("  Username: admin2       | Password: admin2")

print("\nSTUDENTS:")
print("  ID: 3  | Username: hardik    | Password: 12")
print("  ID: 4  | Username: student1  | Password: pass1")
print("  ID: 5  | Username: student2  | Password: pass2")
print("  ID: 6  | Username: student3  | Password: pass3")
print("  ID: 7  | Username: student4  | Password: pass4")
print("  ID: 8  | Username: student5  | Password: pass5")

print("\n" + "=" * 70)
print("✓ SEED DATA CREATION COMPLETE!")
print("=" * 70)
