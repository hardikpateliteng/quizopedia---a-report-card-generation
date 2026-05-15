import os
import django
import random
from django.utils import timezone
from datetime import timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stu_test.settings')
django.setup()

from quiz.models import CustomUser, Subject, Quiz, Question, Option, QuizAttempt, StudentAnswer, Certificate

def run():
    print("Clearing database...")
    CustomUser.objects.all().delete()
    Subject.objects.all().delete()

    print("Creating admin user...")
    CustomUser.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin',
        user_type='admin',
        first_name='System',
        last_name='Admin'
    )

    print("Creating subjects...")
    subjects_data = ['Computer Science', 'Mathematics', 'Physics', 'History']
    subjects = []
    for s_name in subjects_data:
        sub = Subject.objects.create(name=s_name, description=f"All about {s_name}")
        subjects.append(sub)

    print("Creating quizzes and questions...")
    quizzes = []
    
    # Quiz 1: Python Basics
    q1 = Quiz.objects.create(title='Python Basics', subject=subjects[0], time_limit_minutes=15, is_active=True)
    quizzes.append(q1)
    
    # Python Questions
    python_qs = [
        ("What is the output of `print(2 ** 3)`?", ["8", "6", "9", "Error"], "8"),
        ("Which keyword is used to define a function?", ["def", "function", "fun", "define"], "def"),
        ("What data type is `[1, 2, 3]`?", ["List", "Tuple", "Set", "Dictionary"], "List"),
        ("Which of these is NOT a Python framework?", ["Laravel", "Django", "Flask", "FastAPI"], "Laravel"),
        ("How do you start a comment in Python?", ["#", "//", "<!--", "/*"], "#")
    ]
    for q_text, options, correct in python_qs:
        question = Question.objects.create(quiz=q1, text=q_text, marks=10)
        for opt in options:
            Option.objects.create(question=question, text=opt, is_correct=(opt == correct))

    # Quiz 2: Advanced Math
    q2 = Quiz.objects.create(title='Calculus Fundamentals', subject=subjects[1], time_limit_minutes=20, is_active=True)
    quizzes.append(q2)
    
    math_qs = [
        ("What is the derivative of x^2?", ["2x", "x", "2", "x^2/2"], "2x"),
        ("What is the integral of 2x?", ["x^2 + C", "x^2", "2x^2 + C", "none of the above"], "x^2 + C"),
        ("What is 5! (factorial)?", ["120", "24", "600", "15"], "120"),
        ("What is the value of pi to two decimal places?", ["3.14", "3.15", "3.12", "3.16"], "3.14"),
        ("If y = 3x + 2, what is the slope?", ["3", "2", "1", "-2"], "3")
    ]
    for q_text, options, correct in math_qs:
        question = Question.objects.create(quiz=q2, text=q_text, marks=10)
        for opt in options:
            Option.objects.create(question=question, text=opt, is_correct=(opt == correct))

    # Quiz 3: World History
    q3 = Quiz.objects.create(title='20th Century History', subject=subjects[3], time_limit_minutes=15, is_active=True)
    quizzes.append(q3)
    
    hist_qs = [
        ("In what year did World War II end?", ["1945", "1939", "1914", "1918"], "1945"),
        ("Who was the first person in space?", ["Yuri Gagarin", "Neil Armstrong", "Buzz Aldrin", "John Glenn"], "Yuri Gagarin"),
        ("When did the Titanic sink?", ["1912", "1905", "1923", "1898"], "1912"),
        ("Who invented the telephone?", ["Alexander Graham Bell", "Thomas Edison", "Nikola Tesla", "Albert Einstein"], "Alexander Graham Bell"),
        ("Which empire was known as 'the empire on which the sun never sets'?", ["British Empire", "Roman Empire", "Ottoman Empire", "Mongol Empire"], "British Empire")
    ]
    for q_text, options, correct in hist_qs:
        question = Question.objects.create(quiz=q3, text=q_text, marks=10)
        for opt in options:
            Option.objects.create(question=question, text=opt, is_correct=(opt == correct))

    print("Creating 15 students...")
    first_names = ["Emma", "Liam", "Olivia", "Noah", "Ava", "William", "Sophia", "James", "Isabella", "Benjamin", "Mia", "Lucas", "Charlotte", "Henry", "Amelia"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson"]
    
    students = []
    for i in range(15):
        fname = first_names[i]
        lname = last_names[i]
        enrollment = f"STU2026{str(i+1).zfill(3)}"
        
        student = CustomUser.objects.create_user(
            username=enrollment,
            email=f"{fname.lower()}.{lname.lower()}@college.edu",
            password="password123",
            user_type='student',
            enrollment_no=enrollment,
            first_name=fname,
            last_name=lname,
            branch=random.choice(["Computer Science", "Information Tech", "Mechanical", "Electrical"]),
            proctor=random.choice(["Dr. Allen", "Prof. Carter", "Dr. White", "Prof. Harris"]),
            attendance=random.randint(60, 100),
            cgpa=round(random.uniform(5.5, 9.8), 2)
        )
        students.append(student)

    print("Creating random quiz attempts for students...")
    now = timezone.now()
    
    for student in students:
        # Each student takes 1 to 3 quizzes
        num_quizzes = random.randint(1, 3)
        quizzes_taken = random.sample(quizzes, num_quizzes)
        
        for quiz in quizzes_taken:
            # Random performance: 40% to 100% correct rate target
            target_accuracy = random.uniform(0.4, 1.0)
            
            # Start time somewhere in the last 14 days
            start_time = now - timedelta(days=random.randint(0, 14), hours=random.randint(1, 23))
            time_taken = random.randint(300, quiz.time_limit_minutes * 60) # Random time in seconds
            end_time = start_time + timedelta(seconds=time_taken)
            
            attempt = QuizAttempt.objects.create(
                student=student,
                quiz=quiz,
                score=0,
                tab_switches=random.choice([0, 0, 0, 1, 1, 2]), # Mostly 0, sometimes 1 or 2
                time_taken_seconds=time_taken,
                is_completed=True,
                start_time=start_time,
                end_time=end_time
            )
            
            score = 0
            answers_to_create = []
            
            # Answer questions
            for question in quiz.questions.all():
                options = list(question.options.all())
                
                if random.random() <= target_accuracy:
                    # Pick correct option
                    selected = next(opt for opt in options if opt.is_correct)
                else:
                    # Pick random wrong option
                    wrong_options = [opt for opt in options if not opt.is_correct]
                    selected = random.choice(wrong_options) if wrong_options else random.choice(options)
                
                if selected.is_correct:
                    score += question.marks
                    
                answers_to_create.append(StudentAnswer(
                    attempt=attempt,
                    question=question,
                    selected_option=selected,
                    is_correct=selected.is_correct
                ))
            
            StudentAnswer.objects.bulk_create(answers_to_create)
            
            attempt.score = score
            attempt.save()
            
            # Auto-generate certificate if passing grade >= 40%
            if (score / quiz.total_marks) >= 0.40:
                Certificate.objects.get_or_create(attempt=attempt)
                
    print("--------------------------------------------------")
    print("Database seeded successfully!")
    print("Admin Email: admin@example.com OR admin")
    print("Admin Password: admin")
    print("Student Passwords: password123 (Format: STU2026001, STU2026002...)")
    print("--------------------------------------------------")

if __name__ == '__main__':
    run()
