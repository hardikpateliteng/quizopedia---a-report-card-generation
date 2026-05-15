from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('student', 'Student'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='student')

    # Student-specific fields
    enrollment_no = models.CharField(max_length=100, blank=True, null=True, unique=True)
    attendance = models.PositiveIntegerField(default=0)
    cgpa = models.FloatField("CGPA", default=0.0)
    review = models.IntegerField(default=0)
    branch = models.CharField(max_length=100, blank=True, null=True)
    proctor = models.CharField(max_length=100, blank=True, null=True)
    can_edit_profile = models.BooleanField(default=False)

    # Extended profile fields
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    semester = models.PositiveIntegerField(blank=True, null=True)
    year = models.CharField(max_length=20, blank=True, null=True)
    section = models.CharField(max_length=10, blank=True, null=True)
    roll_number = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Other')
    admission_year = models.PositiveIntegerField(blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.username

    @property
    def total_score(self):
        from django.db.models import Sum
        return self.attempts.aggregate(total=Sum('score'))['total'] or 0

    @property
    def quizzes_attempted(self):
        return self.attempts.filter(is_completed=True).count()

    @property
    def average_score_percent(self):
        attempts = self.attempts.filter(is_completed=True)
        if not attempts.exists():
            return 0
        total_pct = 0
        count = 0
        for attempt in attempts:
            total_marks = sum(q.marks for q in attempt.quiz.questions.all())
            if total_marks > 0:
                total_pct += (attempt.score / total_marks) * 100
                count += 1
        return round(total_pct / count, 1) if count else 0


class Subject(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Quiz(models.Model):
    title = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='quizzes')
    description = models.TextField(blank=True, null=True)
    time_limit_minutes = models.PositiveIntegerField(default=30)
    max_questions = models.IntegerField(default=10)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def total_marks(self):
        return sum(q.marks for q in self.questions.all())

    @property
    def question_count(self):
        return self.questions.count()

    @property
    def avg_score(self):
        attempts = self.attempts.filter(is_completed=True)
        if not attempts.exists():
            return 0
        return round(attempts.aggregate(avg=models.Avg('score'))['avg'] or 0, 1)


class Question(models.Model):
    QUESTION_TYPES = (
        ('MCQ', 'Multiple Choice'),
        ('TF', 'True/False'),
    )
    DIFFICULTY_LEVELS = (
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    )
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, null=True, blank=True, related_name='questions')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES, default='MCQ')
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_LEVELS, default='Medium')
    image = models.ImageField(upload_to='question_images/', blank=True, null=True)
    marks = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.question_text[:60]

    @property
    def correct_rate(self):
        """Percentage of students who got this question correct."""
        total = StudentAnswer.objects.filter(question=self).count()
        if not total:
            return None
        correct = StudentAnswer.objects.filter(question=self, is_correct=True).count()
        return round((correct / total) * 100, 1)


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=512)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.option_text

    @property
    def text(self):
        return self.option_text

    @text.setter
    def text(self, value):
        self.option_text = value


class QuizAttempt(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)
    time_taken_seconds = models.PositiveIntegerField(default=0)
    score = models.FloatField(default=0.0)
    is_completed = models.BooleanField(default=False)
    tab_switches = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.student.username} — {self.quiz.title}"

    @property
    def total_marks(self):
        return self.quiz.total_marks

    @property
    def percentage(self):
        tm = self.total_marks
        return round((self.score / tm * 100), 1) if tm > 0 else 0

    @property
    def grade(self):
        p = self.percentage
        if p >= 90: return 'A+'
        if p >= 80: return 'A'
        if p >= 70: return 'B'
        if p >= 60: return 'C'
        if p >= 40: return 'D'
        return 'F'


class StudentAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(Option, on_delete=models.SET_NULL, blank=True, null=True)
    is_correct = models.BooleanField(default=False)


class Certificate(models.Model):
    attempt = models.OneToOneField(QuizAttempt, on_delete=models.CASCADE, related_name='certificate')
    cert_number = models.CharField(max_length=50, unique=True, default='')
    issued_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.cert_number:
            self.cert_number = f"QA-{self.attempt.student.enrollment_no or self.attempt.student.id}-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.cert_number


class ContactQuery(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
