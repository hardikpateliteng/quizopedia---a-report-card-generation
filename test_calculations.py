import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stu_test.settings')
django.setup()

from quiz.models import CustomUser, Quiz, QuizAttempt, Question, Option, StudentAnswer

def test_quiz_calculations():
    # Get the student
    student = CustomUser.objects.get(username='student1')
    print(f"Student: {student.username}")

    # Get the math quiz
    math_quiz = Quiz.objects.get(title='Mathematics Quiz')
    print(f"Quiz: {math_quiz.title}")
    print(f"Total marks: {math_quiz.total_marks}")
    print(f"Questions: {math_quiz.question_count}")

    # Simulate taking the quiz - answer all correctly
    attempt = QuizAttempt.objects.create(
        student=student,
        quiz=math_quiz,
        score=0,
        time_taken_seconds=300,
        is_completed=True
    )

    score = 0
    answers = []

    for question in math_quiz.questions.all():
        print(f"Question: {question.question_text}, marks: {question.marks}")
        # Get correct option
        correct_option = question.options.filter(is_correct=True).first()
        print(f"Correct option: {correct_option.option_text}")

        # Simulate correct answer
        score += question.marks
        answers.append(StudentAnswer(
            attempt=attempt,
            question=question,
            selected_option=correct_option,
            is_correct=True
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
    test_quiz_calculations()