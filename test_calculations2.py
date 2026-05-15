import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stu_test.settings')
django.setup()

from quiz.models import CustomUser, Quiz, QuizAttempt, Question, Option, StudentAnswer

def test_quiz_calculations_partial():
    # Get the student
    student = CustomUser.objects.get(username='student1')

    # Get the python quiz
    python_quiz = Quiz.objects.get(title='Python Quiz')
    print(f"Quiz: {python_quiz.title}")
    print(f"Total marks: {python_quiz.total_marks}")

    # Simulate taking the quiz - answer 2 correctly, 1 wrong
    attempt = QuizAttempt.objects.create(
        student=student,
        quiz=python_quiz,
        score=0,
        time_taken_seconds=400,
        is_completed=True
    )

    score = 0
    answers = []
    questions = list(python_quiz.questions.all())

    # Answer first 2 correctly
    for i in range(2):
        question = questions[i]
        correct_option = question.options.filter(is_correct=True).first()
        score += question.marks
        answers.append(StudentAnswer(
            attempt=attempt,
            question=question,
            selected_option=correct_option,
            is_correct=True
        ))

    # Answer last one wrong
    question = questions[2]
    wrong_options = question.options.filter(is_correct=False)
    wrong_option = wrong_options.first()
    answers.append(StudentAnswer(
        attempt=attempt,
        question=question,
        selected_option=wrong_option,
        is_correct=False
    ))

    attempt.score = score
    attempt.save()

    StudentAnswer.objects.bulk_create(answers)

    print(f"Attempt score: {attempt.score}")
    print(f"Total marks: {attempt.total_marks}")
    print(f"Percentage: {attempt.percentage}%")
    print(f"Grade: {attempt.grade}")

    # Test average score
    print(f"Student total score across all attempts: {student.total_score}")
    print(f"Student quizzes attempted: {student.quizzes_attempted}")
    print(f"Student average score percent: {student.average_score_percent}%")

if __name__ == '__main__':
    test_quiz_calculations_partial()