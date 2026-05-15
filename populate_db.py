import os
import django
import random
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stu_test.settings')
django.setup()

from quiz.models import CustomUser, Subject, Quiz, Question, Option, QuizAttempt, StudentAnswer

def populate():
    print("Clearing old test data...")
    CustomUser.objects.filter(user_type='student', username__startswith='teststudent').delete()
    Quiz.objects.filter(title="Sample Python Quiz").delete()
    Subject.objects.filter(name="Python Programming").delete()

    print("Creating Subject...")
    subject = Subject.objects.create(name="Python Programming")

    print("Creating 5 students...")
    students = []
    for i in range(1, 6):
        student = CustomUser.objects.create_user(
            username=f'teststudent{i}',
            email=f'teststudent{i}@example.com',
            password='password123',
            user_type='student',
            enrollment_no=f'ENR202600{i}',
            attendance=random.choice([85, 90, 95, 100]),
            cgpa=round(random.uniform(7.0, 10.0), 2),
            review=random.randint(3, 5)
        )
        students.append(student)

    print("Creating 1 Quiz...")
    quiz = Quiz.objects.create(
        title="Sample Python Quiz",
        subject=subject,
        description="A basic quiz to test Python knowledge.",
        time_limit_minutes=15
    )

    print("Creating 5 Questions and Options...")
    questions_data = [
        ("What is the output of `print(2 ** 3)`?", [("6", False), ("8", True), ("9", False), ("12", False)]),
        ("Which keyword is used to define a function in Python?", [("func", False), ("define", False), ("def", True), ("function", False)]),
        ("What data type is `[1, 2, 3]`?", [("Tuple", False), ("Set", False), ("Dictionary", False), ("List", True)]),
        ("How do you insert comments in Python code?", [("// comment", False), ("/* comment */", False), ("# comment", True), ("-- comment", False)]),
        ("Which space is used for indentation in Python conventionally?", [("1 space", False), ("2 spaces", False), ("4 spaces", True), ("8 spaces", False)])
    ]

    questions = []
    for q_text, options_data in questions_data:
        question = Question.objects.create(quiz=quiz, question_text=q_text, marks=2)
        questions.append(question)
        for opt_text, is_comp in options_data:
            Option.objects.create(question=question, option_text=opt_text, is_correct=is_comp)

    print("Creating some Quiz Attempts...")
    # Student 1 takes the quiz and gets everything right
    attempt1 = QuizAttempt.objects.create(student=students[0], quiz=quiz, score=10.0, is_completed=True, start_time=timezone.now(), end_time=timezone.now())
    for q in questions:
        correct_opt = Option.objects.get(question=q, is_correct=True)
        StudentAnswer.objects.create(attempt=attempt1, question=q, selected_option=correct_opt, is_correct=True)

    # Student 2 takes the quiz and gets some right
    attempt2 = QuizAttempt.objects.create(student=students[1], quiz=quiz, score=6.0, is_completed=True, tab_switches=2, start_time=timezone.now(), end_time=timezone.now())
    for i, q in enumerate(questions):
        # Gets first 3 correct, last 2 wrong
        if i < 3:
            opt = Option.objects.get(question=q, is_correct=True)
            is_c = True
        else:
            opt = Option.objects.filter(question=q, is_correct=False).first()
            is_c = False
        StudentAnswer.objects.create(attempt=attempt2, question=q, selected_option=opt, is_correct=is_c)

    print("Database populated successfully!")

if __name__ == '__main__':
    populate()
