import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stu_test.settings')
django.setup()

from quiz.models import Subject, Quiz, Question, Option

def run():
    print("Deleting all existing quizzes, questions, and options...")

    # Delete in reverse order to avoid cascade issues
    Quiz.objects.all().delete()
    Question.objects.filter(quiz__isnull=True).delete()  # Delete orphaned questions
    Subject.objects.all().delete()

    print("Creating subjects...")
    math_subject = Subject.objects.create(name='Mathematics', description='Mathematics quiz')
    python_subject = Subject.objects.create(name='Python', description='Python programming quiz')

    print("Creating Mathematics quiz...")
    math_quiz = Quiz.objects.create(
        title='Mathematics Quiz',
        subject=math_subject,
        description='Basic mathematics questions',
        time_limit_minutes=30,
        max_questions=3,
        is_active=True
    )

    print("Adding questions to Mathematics quiz...")
    # Question 1
    q1 = Question.objects.create(
        quiz=math_quiz,
        subject=math_subject,
        question_text='What is 2 + 2?',
        question_type='MCQ',
        difficulty='Easy',
        marks=1
    )
    Option.objects.create(question=q1, option_text='3', is_correct=False)
    Option.objects.create(question=q1, option_text='4', is_correct=True)
    Option.objects.create(question=q1, option_text='5', is_correct=False)
    Option.objects.create(question=q1, option_text='6', is_correct=False)

    # Question 2
    q2 = Question.objects.create(
        quiz=math_quiz,
        subject=math_subject,
        question_text='What is the square root of 16?',
        question_type='MCQ',
        difficulty='Easy',
        marks=1
    )
    Option.objects.create(question=q2, option_text='2', is_correct=False)
    Option.objects.create(question=q2, option_text='4', is_correct=True)
    Option.objects.create(question=q2, option_text='8', is_correct=False)
    Option.objects.create(question=q2, option_text='16', is_correct=False)

    # Question 3
    q3 = Question.objects.create(
        quiz=math_quiz,
        subject=math_subject,
        question_text='What is 10 * 5?',
        question_type='MCQ',
        difficulty='Easy',
        marks=1
    )
    Option.objects.create(question=q3, option_text='40', is_correct=False)
    Option.objects.create(question=q3, option_text='50', is_correct=True)
    Option.objects.create(question=q3, option_text='60', is_correct=False)
    Option.objects.create(question=q3, option_text='70', is_correct=False)

    print("Creating Python quiz...")
    python_quiz = Quiz.objects.create(
        title='Python Quiz',
        subject=python_subject,
        description='Basic Python programming questions',
        time_limit_minutes=30,
        max_questions=3,
        is_active=True
    )

    print("Adding questions to Python quiz...")
    # Question 1
    q4 = Question.objects.create(
        quiz=python_quiz,
        subject=python_subject,
        question_text='What is the output of print(2 + 3)?',
        question_type='MCQ',
        difficulty='Easy',
        marks=1
    )
    Option.objects.create(question=q4, option_text='2+3', is_correct=False)
    Option.objects.create(question=q4, option_text='5', is_correct=True)
    Option.objects.create(question=q4, option_text='23', is_correct=False)
    Option.objects.create(question=q4, option_text='Error', is_correct=False)

    # Question 2
    q5 = Question.objects.create(
        quiz=python_quiz,
        subject=python_subject,
        question_text='Which keyword is used to define a function in Python?',
        question_type='MCQ',
        difficulty='Easy',
        marks=1
    )
    Option.objects.create(question=q5, option_text='function', is_correct=False)
    Option.objects.create(question=q5, option_text='def', is_correct=True)
    Option.objects.create(question=q5, option_text='func', is_correct=False)
    Option.objects.create(question=q5, option_text='define', is_correct=False)

    # Question 3
    q6 = Question.objects.create(
        quiz=python_quiz,
        subject=python_subject,
        question_text='What is the data type of [1, 2, 3]?',
        question_type='MCQ',
        difficulty='Easy',
        marks=1
    )
    Option.objects.create(question=q6, option_text='Tuple', is_correct=False)
    Option.objects.create(question=q6, option_text='List', is_correct=True)
    Option.objects.create(question=q6, option_text='Set', is_correct=False)
    Option.objects.create(question=q6, option_text='Dictionary', is_correct=False)

    print("Setup complete!")
    print(f"Mathematics Quiz ID: {math_quiz.id}")
    print(f"Python Quiz ID: {python_quiz.id}")

if __name__ == '__main__':
    run()