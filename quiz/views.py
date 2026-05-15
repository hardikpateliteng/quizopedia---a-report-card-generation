"""
Quiz Academy — Views
All admin and student views. Organized by role.
"""
import csv
import os
import uuid
import random
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.http import url_has_allowed_host_and_scheme
from django.db.models import Count, Sum, Avg, Q, F
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

from quiz.models import (
    CustomUser, Quiz, Question, Subject,
    Option, QuizAttempt, StudentAnswer, Certificate
)
from quiz.forms import (
    QuizForm, QuestionForm, AddQuestionForm, OptionForm, StudentProfileForm,
    AdminStudentCreateForm, AdminStudentEditForm, ForgotPasswordForm, OTPVerificationForm
)


# ============================================================
# SHARED / HOME
# ============================================================

def _clone_question_to_quiz(source_question, quiz):
    cloned = Question.objects.create(
        quiz=quiz,
        subject=quiz.subject,
        question_text=source_question.question_text,
        question_type=source_question.question_type,
        difficulty=source_question.difficulty,
        image=source_question.image,
        marks=source_question.marks,
    )
    source_options = source_question.options.all().order_by('id')
    Option.objects.bulk_create([
        Option(
            question=cloned,
            option_text=opt.option_text,
            is_correct=opt.is_correct,
        )
        for opt in source_options
    ])
    return cloned


def _auto_attach_questions_to_quiz(quiz):
    linked_questions = Question.objects.filter(quiz=quiz)
    existing_count = linked_questions.count()
    if existing_count >= quiz.max_questions:
        return

    needed = quiz.max_questions - existing_count
    existing_texts = set(linked_questions.values_list('question_text', flat=True))

    # 1) Prefer subject pool questions not yet linked to a quiz.
    pool_questions = Question.objects.filter(
        subject=quiz.subject,
        quiz__isnull=True,
    ).exclude(question_text__in=existing_texts).order_by('id')

    for source in pool_questions[:needed]:
        _clone_question_to_quiz(source, quiz)
        existing_texts.add(source.question_text)
        needed -= 1
        if needed <= 0:
            return

    # 2) Legacy fallback: clone same-subject questions already linked elsewhere.
    subject_questions = Question.objects.filter(
        subject=quiz.subject,
    ).exclude(quiz=quiz).exclude(question_text__in=existing_texts).order_by('id')

    for source in subject_questions[:needed]:
        _clone_question_to_quiz(source, quiz)
        existing_texts.add(source.question_text)
        needed -= 1
        if needed <= 0:
            return

    # 3) Extra legacy recovery: if subject was newly created, infer from quiz title/subject text.
    keyword = (quiz.subject.name or '').strip()
    if not keyword:
        return
    legacy_questions = Question.objects.filter(
        quiz__title__icontains=keyword
    ).exclude(quiz=quiz).exclude(question_text__in=existing_texts).order_by('id')

    for source in legacy_questions[:needed]:
        _clone_question_to_quiz(source, quiz)
        needed -= 1
        if needed <= 0:
            return


def home_view(request):
    if request.user.is_authenticated:
        if request.user.user_type == 'admin':
            return redirect('index1')
        return redirect('stu_index')
    # Render student login page for unauthenticated users
    msg = ''
    if request.method == 'POST':
        enroll_no = request.POST.get('enroll_no', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, enrollment_no=enroll_no, password=password)
        if user is not None and user.user_type == 'student':
            auth_login(request, user)
            return redirect('stu_index')
        msg = "Invalid Enrollment Number or Password."
    return render(request, 'stu_login.html', {'msg': msg})


# ============================================================
# ADMIN AUTH
# ============================================================

def LoginUserView(request):
    msg = ''
    if request.method == 'POST':
        identifier = request.POST.get('identifier', request.POST.get('email', '')).strip()
        password = request.POST.get('password', '')

        # Accept either email or username on admin login.
        if '@' in identifier:
            user = authenticate(request, email=identifier, password=password)
        else:
            user = authenticate(request, username=identifier, password=password)
        if user is not None and user.user_type == 'admin':
            auth_login(request, user)
            return redirect('index1')
        msg = "Invalid username/email or password."
    return render(request, 'sign.html', {'msg': msg})


def logout_admin(request):
    auth_logout(request)
    return redirect('sign1')


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@login_required(login_url='sign1')
def index(request):
    if request.user.user_type != 'admin':
        return redirect('sign1')

    students = CustomUser.objects.filter(user_type='student').annotate(
        score_sum=Sum('attempts__score'),
        quiz_count=Count('attempts')
    )
    total_students = students.count()
    total_quizzes = Quiz.objects.count()
    total_questions = Question.objects.count()
    total_attempts = QuizAttempt.objects.filter(is_completed=True).count()

    # Average score across all completed attempts
    avg_pct = 0
    completed = QuizAttempt.objects.filter(is_completed=True).select_related('quiz')
    if completed.exists():
        pct_sum = 0
        pct_count = 0
        for att in completed:
            tm = att.total_marks
            if tm > 0:
                pct_sum += (att.score / tm) * 100
                pct_count += 1
        avg_pct = round(pct_sum / pct_count, 1) if pct_count else 0

    context = {
        'n': request.user,
        'c': total_students,
        'q': total_questions,
        'total_quizzes': total_quizzes,
        'total_attempts': total_attempts,
        'avg_pct': avg_pct,
        'data': students,
    }
    return render(request, 'index.html', context)


# ============================================================
# ADMIN ANALYTICS
# ============================================================

@login_required(login_url='sign1')
def admin_analytics(request):
    if request.user.user_type != 'admin':
        return redirect('sign1')

    # Core counts
    total_students = CustomUser.objects.filter(user_type='student').count()
    total_quizzes = Quiz.objects.count()
    active_quizzes = Quiz.objects.filter(is_active=True).count()
    total_attempts = QuizAttempt.objects.filter(is_completed=True).count()

    # Average score percentage
    avg_pct = 0
    completed = QuizAttempt.objects.filter(is_completed=True).select_related('quiz')
    pct_values = []
    for att in completed:
        tm = att.total_marks
        if tm > 0:
            pct_values.append((att.score / tm) * 100)
    if pct_values:
        avg_pct = round(sum(pct_values) / len(pct_values), 1)

    # Top 5 performers (by avg percentage across attempts)
    students = CustomUser.objects.filter(user_type='student').annotate(
        quiz_count=Count('attempts'),
        score_sum=Sum('attempts__score')
    ).filter(quiz_count__gt=0)

    top_performers = []
    for s in students:
        top_performers.append({
            'student': s,
            'avg_pct': s.average_score_percent,
            'quiz_count': s.quiz_count,
        })
    top_performers = sorted(top_performers, key=lambda x: x['avg_pct'], reverse=True)[:5]

    # Hardest questions (lowest correct_rate among those with ≥2 answers)
    hardest_questions = []
    for q in Question.objects.all():
        total_ans = StudentAnswer.objects.filter(question=q).count()
        if total_ans >= 1:
            correct_ans = StudentAnswer.objects.filter(question=q, is_correct=True).count()
            rate = round((correct_ans / total_ans) * 100, 1)
            hardest_questions.append({'question': q, 'rate': rate, 'total': total_ans})
    hardest_questions = sorted(hardest_questions, key=lambda x: x['rate'])[:5]

    # Subject-wise quiz count
    subjects = Subject.objects.annotate(quiz_count=Count('quizzes'))

    # Per-quiz avg score
    quiz_stats = []
    for quiz in Quiz.objects.all():
        attempts = QuizAttempt.objects.filter(quiz=quiz, is_completed=True)
        attempt_count = attempts.count()
        if attempt_count > 0:
            avg = round(sum((a.score / a.total_marks * 100) for a in attempts if a.total_marks > 0) / attempt_count, 1)
        else:
            avg = 0
        quiz_stats.append({'quiz': quiz, 'attempts': attempt_count, 'avg_pct': avg})

    context = {
        'total_students': total_students,
        'total_quizzes': total_quizzes,
        'active_quizzes': active_quizzes,
        'total_attempts': total_attempts,
        'avg_pct': avg_pct,
        'top_performers': top_performers,
        'hardest_questions': hardest_questions,
        'subjects': subjects,
        'quiz_stats': quiz_stats,
    }
    return render(request, 'admin_analytics.html', context)


# ============================================================
# ADMIN STUDENT VIEWS
# ============================================================

@login_required(login_url='sign1')
def add_student(request):
    if request.user.user_type != 'admin':
        return redirect('sign1')

    msg = ''
    msg_type = 'danger'
    form = AdminStudentCreateForm()

    if request.method == 'POST':
        form = AdminStudentCreateForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save()
            msg = f"Student '{student.first_name or student.username}' registered successfully!"
            msg_type = 'success'
            form = AdminStudentCreateForm()
        else:
            msg = "Please fix the highlighted errors."

    return render(request, 'Add_student.html', {'s': msg, 'msg_type': msg_type, 'form': form})


@login_required(login_url='sign1')
def admin_student_detail(request, student_id):
    if request.user.user_type != 'admin':
        return redirect('sign1')

    student = get_object_or_404(CustomUser, id=student_id, user_type='student')
    attempts = QuizAttempt.objects.filter(
        student=student, is_completed=True
    ).select_related('quiz').order_by('-start_time')

    attempt_data = []
    for att in attempts:
        attempt_data.append({
            'attempt': att,
            'percentage': att.percentage,
            'grade': att.grade,
            'total_marks': att.total_marks,
        })

    context = {
        'student': student,
        'attempt_data': attempt_data,
        'total_attempts': len(attempt_data),
        'avg_pct': student.average_score_percent,
    }
    return render(request, 'admin_student_detail.html', context)


@login_required(login_url='sign1')
def edit_student_profile(request, student_id):
    if request.user.user_type != 'admin':
        return redirect('sign1')

    student = get_object_or_404(CustomUser, id=student_id, user_type='student')
    msg = ''
    msg_type = 'success'

    if request.method == 'POST':
        form = AdminStudentEditForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            msg = "Student profile updated successfully."
        else:
            msg = "Please fix the highlighted errors."
            msg_type = 'danger'
    else:
        form = AdminStudentEditForm(instance=student)

    return render(request, 'admin_edit_student.html', {
        'form': form,
        'student': student,
        'msg': msg,
        'msg_type': msg_type,
    })


@login_required(login_url='sign1')
def toggle_student_profile_permission(request, student_id):
    if request.user.user_type != 'admin':
        return redirect('sign1')

    if request.method != 'POST':
        return redirect('admin_student_detail', student_id=student_id)

    student = get_object_or_404(CustomUser, id=student_id, user_type='student')
    student.can_edit_profile = not student.can_edit_profile
    student.save(update_fields=['can_edit_profile'])
    return redirect('admin_student_detail', student_id=student_id)


@login_required(login_url='sign1')
def delete_student(request, student_id):
    if request.user.user_type != 'admin':
        return redirect('sign1')

    if request.method != 'POST':
        return redirect('studentreport1')

    student = get_object_or_404(CustomUser, id=student_id, user_type='student')
    student_name = (f"{student.first_name} {student.last_name}".strip() or student.username)
    student.delete()
    messages.success(request, f"Student '{student_name}' was deleted successfully.")

    next_url = request.POST.get('next', '').strip()
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
    return redirect('studentreport1')


@login_required(login_url='sign1')
def student_data(request):
    if request.user.user_type != 'admin':
        return redirect('sign1')

    students = CustomUser.objects.filter(user_type='student').annotate(
        quiz_count=Count('attempts'),
        total_score_agg=Sum('attempts__score')
    ).order_by('first_name', 'username')

    return render(request, 'student_data.html', {
        'students': students,
    })


@login_required(login_url='sign1')
def student_report(request):
    if request.user.user_type != 'admin':
        return redirect('sign1')

    students = CustomUser.objects.filter(user_type='student').annotate(
        quiz_count=Count('attempts'),
        total_score_agg=Sum('attempts__score')
    ).order_by('first_name', 'username')
    student_data = []
    for s in students:
        student_data.append({
            'student': s,
            'quiz_count': s.quiz_count,
            'total_score': s.total_score_agg or 0,
            'avg_pct': s.average_score_percent,
        })

    return render(request, 'studentreport.html', {
        'students': students,
        'student_data': student_data,
    })


@login_required(login_url='sign1')
def download_student_report_csv(request, student_id):
    if request.user.user_type != 'admin':
        return redirect('sign1')

    student = get_object_or_404(CustomUser, id=student_id, user_type='student')
    attempts = QuizAttempt.objects.filter(
        student=student, is_completed=True
    ).select_related('quiz').order_by('-start_time')

    response = HttpResponse(content_type='text/csv')
    filename = f"{student.first_name or student.username}_report.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(['Student', 'Enrollment', 'Branch', 'CGPA'])
    writer.writerow([
        f"{student.first_name} {student.last_name}".strip() or student.username,
        student.enrollment_no or '—',
        student.branch or '—',
        student.cgpa
    ])
    writer.writerow([])
    writer.writerow(['Quiz Title', 'Score', 'Total Marks', 'Percentage', 'Grade', 'Date Attempted', 'Tab Switches'])

    for attempt in attempts:
        total_marks = attempt.total_marks
        writer.writerow([
            attempt.quiz.title,
            attempt.score,
            total_marks,
            f"{attempt.percentage}%",
            attempt.grade,
            attempt.start_time.strftime('%Y-%m-%d %H:%M'),
            attempt.tab_switches,
        ])

    return response


# ============================================================
# ADMIN QUIZ MANAGEMENT
# ============================================================

@login_required(login_url='sign1')
def create_quiz(request):
    if request.user.user_type != 'admin':
        return redirect('sign1')

    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            new_subject_name = form.cleaned_data.get('new_subject', '')
            if new_subject_name:
                subject = Subject.objects.filter(name__iexact=new_subject_name).first()
                if subject is None:
                    subject = Subject.objects.create(name=new_subject_name)
            else:
                subject = form.cleaned_data.get('subject')
            quiz.subject = subject
            quiz.save()
            _auto_attach_questions_to_quiz(quiz)
            return redirect('viewquiz')
    else:
        form = QuizForm()

    return render(request, 'createtest.html', {'form': form})


@login_required(login_url='sign1')
def view_quizzes(request):
    if request.user.user_type != 'admin':
        return redirect('sign1')

    quizzes = Quiz.objects.select_related('subject').annotate(
        attempt_count=Count('attempts')
    ).order_by('-created_at')

    return render(request, 'view_quiz.html', {'quizzes': quizzes})


@login_required(login_url='sign1')
def edit_quiz(request, quiz_id):
    if request.user.user_type != 'admin':
        return redirect('sign1')

    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            updated_quiz = form.save(commit=False)
            new_subject_name = form.cleaned_data.get('new_subject', '')
            if new_subject_name:
                subject = Subject.objects.filter(name__iexact=new_subject_name).first()
                if subject is None:
                    subject = Subject.objects.create(name=new_subject_name)
            else:
                subject = form.cleaned_data.get('subject')
            updated_quiz.subject = subject
            updated_quiz.save()
            _auto_attach_questions_to_quiz(updated_quiz)
            return redirect('viewquiz')
    else:
        form = QuizForm(instance=quiz)

    return render(request, 'createtest.html', {'form': form, 'edit_mode': True, 'quiz': quiz})


@login_required(login_url='sign1')
def delete_quiz(request, quiz_id):
    if request.user.user_type != 'admin':
        return redirect('sign1')

    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == 'POST':
        quiz.delete()
    return redirect('viewquiz')


@login_required(login_url='sign1')
def toggle_quiz(request, quiz_id):
    if request.user.user_type != 'admin':
        return redirect('sign1')

    quiz = get_object_or_404(Quiz, id=quiz_id)
    quiz.is_active = not quiz.is_active
    quiz.save()
    return redirect('viewquiz')


# ============================================================
# ADMIN QUESTION MANAGEMENT
# ============================================================

@login_required(login_url='sign1')
def add_question(request):
    if request.user.user_type != 'admin':
        return redirect('sign1')

    selected_quiz_id = request.GET.get('quiz', '').strip()
    quizzes_with_counts = Quiz.objects.select_related('subject').annotate(
        total_questions=Count('questions')
    ).order_by('-created_at')

    if request.method == 'POST':
        form_action = request.POST.get('form_action', 'add_question')
        selected_quiz_id = request.POST.get('quiz', '').strip()
        form = AddQuestionForm(request.POST, request.FILES)

        if form_action == 'update_limit':
            new_max_questions_raw = (request.POST.get('new_max_questions') or '').strip()
            if not selected_quiz_id.isdigit():
                messages.error(request, "Please select a quiz before setting question limit.")
            else:
                selected_quiz = get_object_or_404(Quiz, id=int(selected_quiz_id))
                question_count = Question.objects.filter(quiz=selected_quiz).count()
                try:
                    new_max_questions = int(new_max_questions_raw)
                except ValueError:
                    messages.error(request, "Please enter a valid maximum question limit.")
                else:
                    if new_max_questions < 1:
                        messages.error(request, "Maximum question limit must be at least 1.")
                    elif new_max_questions < question_count:
                        messages.error(
                            request,
                            f"Maximum question limit cannot be less than added questions ({question_count}).",
                        )
                    else:
                        selected_quiz.max_questions = new_max_questions
                        selected_quiz.save(update_fields=['max_questions'])
                        messages.success(request, "Question limit updated successfully.")
                quizzes_with_counts = Quiz.objects.select_related('subject').annotate(
                    total_questions=Count('questions')
                ).order_by('-created_at')
        elif form.is_valid():
            selected_quiz = form.cleaned_data['quiz']
            if selected_quiz is None:
                form.save()
                messages.success(request, "Question added successfully.")
                return redirect('viewquestion')
            else:
                question_count = Question.objects.filter(quiz=selected_quiz).count()
                if question_count >= selected_quiz.max_questions:
                    messages.error(request, "Question limit reached for this quiz.")
                    form.add_error(None, "Maximum questions reached. Cannot add more questions to this quiz.")
                else:
                    form.save()
                    messages.success(request, "Question added successfully.")
                    return redirect(f"{reverse('viewquestion')}?quiz={selected_quiz.id}")
    else:
        initial = {'question_type': 'MCQ', 'marks': 1}
        if selected_quiz_id and selected_quiz_id.isdigit():
            selected_quiz = quizzes_with_counts.filter(id=int(selected_quiz_id)).first()
            if selected_quiz:
                initial['quiz'] = selected_quiz.id
                if selected_quiz.subject_id:
                    initial['subject'] = selected_quiz.subject.name
        form = AddQuestionForm(initial=initial)

    selected_quiz_obj = None
    max_questions = 0
    current_question_count = 0
    remaining_questions = 0
    limit_reached = False

    if selected_quiz_id and selected_quiz_id.isdigit():
        selected_quiz_obj = quizzes_with_counts.filter(id=int(selected_quiz_id)).first()

    if selected_quiz_obj:
        max_questions = selected_quiz_obj.max_questions
        current_question_count = selected_quiz_obj.total_questions
        remaining_questions = max(max_questions - current_question_count, 0)
        limit_reached = current_question_count >= max_questions

    quiz_limits = {
        str(q.id): {
            'title': q.title,
            'max': q.max_questions,
            'added': q.total_questions,
            'remaining': max(q.max_questions - q.total_questions, 0),
        }
        for q in quizzes_with_counts
    }

    return render(request, 'questionadd.html', {
        'form': form,
        'selected_correct_option': form['correct_option'].value() or '',
        'selected_quiz_id': selected_quiz_id,
        'max_questions': max_questions,
        'current_question_count': current_question_count,
        'remaining_questions': remaining_questions,
        'limit_reached': limit_reached,
        'quiz_limits_json': json.dumps(quiz_limits),
    })


@login_required(login_url='sign1')
def add_option(request, question_id):
    if request.user.user_type != 'admin':
        return redirect('sign1')

    question = get_object_or_404(Question, id=question_id)
    if question.question_type == 'TF':
        return redirect('viewquestion')

    if request.method == 'POST':
        form = OptionForm(request.POST)
        if form.is_valid():
            option = form.save(commit=False)
            option.question = question
            option.save()
            return redirect('viewquestion')
    else:
        form = OptionForm()

    return render(request, 'add_option.html', {'form': form, 'question': question})


@login_required(login_url='sign1')
def view_questions(request):
    if request.user.user_type != 'admin':
        return redirect('sign1')

    quiz_filter = request.GET.get('quiz', '')
    quizzes = Quiz.objects.select_related('subject').annotate(
        total_questions=Count('questions')
    ).order_by('-created_at')

    selected_quiz = None
    questions = Question.objects.none()
    if quiz_filter:
        selected_quiz = get_object_or_404(Quiz, id=quiz_filter)
        questions = Question.objects.filter(quiz=selected_quiz).select_related('quiz').prefetch_related('options')

    return render(request, 'showquestion.html', {
        'al': questions,
        'quizzes': quizzes,
        'selected_quiz_obj': selected_quiz,
        'selected_quiz': quiz_filter,
    })


@login_required(login_url='sign1')
def delete_question(request, question_id):
    if request.user.user_type != 'admin':
        return redirect('sign1')

    question = get_object_or_404(Question, id=question_id)
    quiz_id = question.quiz_id
    if request.method == 'POST':
        question.delete()
    return redirect(f"{reverse('viewquestion')}?quiz={quiz_id}")


# ============================================================
# ADMIN ATTENDANCE & LEADERBOARD
# ============================================================

@login_required(login_url='sign1')
def view_attendance(request):
    if request.user.user_type != 'admin':
        return redirect('sign1')

    students = CustomUser.objects.filter(user_type='student').annotate(
        quiz_count=Count('attempts', filter=Q(attempts__is_completed=True))
    ).order_by('-attendance', 'first_name', 'username')

    return render(request, 'admin_attendance.html', {'students': students})


@login_required
def global_leaderboard(request):
    top_attempts = QuizAttempt.objects.filter(
        is_completed=True
    ).select_related('student', 'quiz').annotate(
        total_marks_calc=Sum('quiz__questions__marks'),
        pct=F('score') / Sum('quiz__questions__marks') * 100
    ).order_by('-pct', 'tab_switches')[:20]

    template_name = 'leaderboard.html' if request.user.user_type == 'admin' else 'stu_leaderboard.html'
    return render(request, template_name, {'attempts': top_attempts})


# ============================================================
# STUDENT AUTH
# ============================================================

def student_login_view(request):
    msg = ''
    if request.method == 'POST':
        enroll_no = request.POST.get('enroll_no', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, enrollment_no=enroll_no, password=password)
        if user is not None and user.user_type == 'student':
            auth_login(request, user)
            return redirect('stu_index')
        msg = "Invalid Enrollment Number or Password."
    return render(request, 'stu_login.html', {'msg': msg})


def student_logout_view(request):
    auth_logout(request)
    return redirect('student_login_view')


# ============================================================
# STUDENT PASSWORD RESET
# ============================================================

def forgot_password_view(request):
    """Step 1: Ask for email and send OTP"""
    if request.user.is_authenticated:
        return redirect('stu_index')

    msg = ''
    msg_type = 'info'
    form = ForgotPasswordForm()

    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            # Check if email exists in students
            try:
                user = CustomUser.objects.get(email=email, user_type='student')
            except CustomUser.DoesNotExist:
                msg = "No student account found with this email."
                msg_type = 'danger'
                return render(request, 'forgot_password.html', {'form': form, 'msg': msg, 'msg_type': msg_type})

            # Generate 6-digit OTP
            otp = random.randint(100000, 999999)

            # Store in session
            request.session['reset_otp'] = str(otp)
            request.session['reset_email'] = email
            request.session.set_expiry(600)  # OTP expires in 10 minutes

            # Send email
            try:
                subject = "Password Reset OTP"
                message = f"""
Hello {user.first_name or 'Student'},

Your OTP for password reset is: {otp}

This OTP is valid for 10 minutes only.

Do not share this OTP with anyone.

Best regards,
Quiz Academy Team
                """
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER or getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                    [email],
                    fail_silently=False,
                )
                email_backend = getattr(settings, 'EMAIL_BACKEND', '')
                if email_backend == 'django.core.mail.backends.console.EmailBackend':
                    msg = f"OTP mode is set to console. OTP {otp} has been printed to the server console."
                else:
                    msg = f"OTP has been sent to {email}. Please check your email."
                msg_type = 'success'
                return redirect('verify_otp_view')
            except Exception as e:
                # If sending fails, show console hint for dev ease.
                email_backend = getattr(settings, 'EMAIL_BACKEND', '')
                if email_backend == 'django.core.mail.backends.console.EmailBackend':
                    otp_hint = f" OTP {otp} was produced and printed in console."
                else:
                    otp_hint = ""
                msg = f"Failed to send email. Please check SMTP config. Error: {str(e)}{otp_hint}"
                msg_type = 'danger'

    context = {
        'form': form,
        'msg': msg,
        'msg_type': msg_type,
    }
    return render(request, 'forgot_password.html', context)


def verify_otp_view(request):
    """Step 2: Verify OTP and collect new password"""
    if request.user.is_authenticated:
        return redirect('stu_index')

    # Check if user has initiated password reset
    otp_from_session = request.session.get('reset_otp')
    email_from_session = request.session.get('reset_email')

    if not otp_from_session or not email_from_session:
        msg = "Session expired. Please start password reset again."
        msg_type = 'danger'
        return render(request, 'verify_otp.html', {'msg': msg, 'msg_type': msg_type, 'form': OTPVerificationForm()})

    msg = ''
    msg_type = 'info'
    form = OTPVerificationForm()

    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp_entered = form.cleaned_data['otp']
            new_password = form.cleaned_data['new_password']

            # Verify OTP
            if str(otp_entered) != str(otp_from_session):
                msg = "Invalid OTP. Please try again."
                msg_type = 'danger'
                return render(request, 'verify_otp.html', {'form': form, 'msg': msg, 'msg_type': msg_type})

            # Update password
            try:
                user = CustomUser.objects.get(email=email_from_session)
                user.set_password(new_password)
                user.save()

                # Clear session
                del request.session['reset_otp']
                del request.session['reset_email']

                msg = "Password reset successfully! Please login with your new password."
                msg_type = 'success'
                return render(request, 'verify_otp.html', {'msg': msg, 'msg_type': msg_type, 'form': OTPVerificationForm(), 'show_login_btn': True})

            except CustomUser.DoesNotExist:
                msg = "User not found."
                msg_type = 'danger'
        else:
            msg_type = 'danger'

    context = {
        'form': form,
        'msg': msg,
        'msg_type': msg_type,
        'email': email_from_session,
    }
    return render(request, 'verify_otp.html', context)


# ============================================================
# STUDENT DASHBOARD & PROFILE
# ============================================================

@login_required(login_url='student_login_view')
def student_dashboard(request):
    if request.user.user_type != 'student':
        return redirect('student_login_view')

    # Filter: only active quizzes
    quizzes = Quiz.objects.filter(is_active=True).select_related('subject').order_by('-created_at')

    # Subject filter
    subject_filter = request.GET.get('subject', '')
    if subject_filter:
        quizzes = quizzes.filter(subject_id=subject_filter)

    subjects = Subject.objects.all()
    attempts = QuizAttempt.objects.filter(student=request.user, is_completed=True).select_related('quiz')
    attempted_quiz_ids = {att.quiz_id for att in attempts}
    total_quizzes = quizzes.count()
    completed_count = quizzes.filter(id__in=attempted_quiz_ids).count()
    pending_count = max(total_quizzes - completed_count, 0)

    context = {
        'quizzes': quizzes,
        'attempts': attempts,
        'attempted_quiz_ids': attempted_quiz_ids,
        'subjects': subjects,
        'selected_subject': subject_filter,
        'total_quizzes': total_quizzes,
        'completed_count': completed_count,
        'pending_count': pending_count,
        'avg_pct': request.user.average_score_percent,
    }
    return render(request, 'stu_index.html', context)


@login_required(login_url='student_login_view')
def student_profile(request):
    if request.user.user_type != 'student':
        return redirect('student_login_view')

    msg = ''
    msg_type = 'success'
    can_edit_profile = request.user.can_edit_profile
    if request.method == 'POST':
        if not can_edit_profile:
            form = StudentProfileForm(instance=request.user)
            msg = "Profile editing is locked. Please contact admin for permission."
            msg_type = 'danger'
        else:
            form = StudentProfileForm(request.POST, request.FILES, instance=request.user)
            if form.is_valid():
                form.save()
                msg = "Profile updated successfully!"
            else:
                msg = "Please fix the errors below."
                msg_type = 'danger'
    else:
        form = StudentProfileForm(instance=request.user)

    if not can_edit_profile:
        for field in form.fields.values():
            field.widget.attrs['disabled'] = 'disabled'

    attempts = QuizAttempt.objects.filter(
        student=request.user, is_completed=True
    ).select_related('quiz').order_by('-start_time')[:5]

    context = {
        'student': request.user,
        'form': form,
        'msg': msg,
        'msg_type': msg_type,
        'recent_attempts': attempts,
        'avg_pct': request.user.average_score_percent,
        'quizzes_attempted': request.user.quizzes_attempted,
        'can_edit_profile': can_edit_profile,
    }
    return render(request, 'stu_profile.html', context)


@login_required(login_url='student_login_view')
def quiz_history(request):
    if request.user.user_type != 'student':
        return redirect('student_login_view')

    attempts = QuizAttempt.objects.filter(
        student=request.user, is_completed=True
    ).select_related('quiz', 'quiz__subject').order_by('-start_time')

    attempt_data = []
    for att in attempts:
        attempt_data.append({
            'attempt': att,
            'percentage': att.percentage,
            'grade': att.grade,
            'total_marks': att.total_marks,
        })

    context = {
        'attempt_data': attempt_data,
        'total': len(attempt_data),
        'avg_pct': request.user.average_score_percent,
    }
    return render(request, 'quiz_history.html', context)


# ============================================================
# STUDENT QUIZ TAKING
# ============================================================

@login_required(login_url='student_login_view')
def take_quiz(request, quiz_id):
    if request.user.user_type != 'student':
        return redirect('student_login_view')

    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)

    # Block re-entry if already completed
    existing = QuizAttempt.objects.filter(student=request.user, quiz=quiz, is_completed=True).first()
    if existing:
        return redirect('quiz_result', quiz_id=quiz.id)

    _auto_attach_questions_to_quiz(quiz)
    questions = Question.objects.filter(quiz=quiz).prefetch_related('options')

    if request.method == 'POST':
        tab_switches = int(request.POST.get('tab_switches', 0))
        time_taken = int(request.POST.get('time_taken', 0))

        # Create attempt
        attempt = QuizAttempt.objects.create(
            student=request.user,
            quiz=quiz,
            score=0,
            tab_switches=tab_switches,
            time_taken_seconds=time_taken,
            is_completed=True,
            end_time=timezone.now(),
        )

        # Calculate score and save answers
        score = 0
        answers = []
        for question in questions:
            selected_option_id = request.POST.get(f'question_{question.id}')
            if selected_option_id:
                try:
                    selected_option = Option.objects.get(id=int(selected_option_id), question=question)
                    is_correct = selected_option.is_correct
                    if is_correct:
                        score += question.marks
                    answers.append(StudentAnswer(
                        attempt=attempt,
                        question=question,
                        selected_option=selected_option,
                        is_correct=is_correct,
                    ))
                except Option.DoesNotExist:
                    pass
            else:
                # Unanswered question — record as skipped
                answers.append(StudentAnswer(
                    attempt=attempt,
                    question=question,
                    selected_option=None,
                    is_correct=False,
                ))

        attempt.score = score
        attempt.save()

        if answers:
            StudentAnswer.objects.bulk_create(answers)

        # Auto-generate certificate if score ≥ 40%
        total_marks = quiz.total_marks
        if total_marks > 0 and (score / total_marks) >= 0.40:
            Certificate.objects.get_or_create(attempt=attempt)

        return redirect('quiz_result', quiz_id=quiz.id)

    context = {
        'quiz': quiz,
        'questions': questions,
    }
    return render(request, 'take_quiz.html', context)


@login_required(login_url='student_login_view')
def quiz_result(request, quiz_id):
    if request.user.user_type != 'student':
        return redirect('student_login_view')

    quiz = get_object_or_404(Quiz, id=quiz_id)
    attempt = get_object_or_404(QuizAttempt, student=request.user, quiz=quiz, is_completed=True)

    # Answer review
    answers = attempt.answers.select_related('question', 'selected_option').prefetch_related('question__options')
    answer_review = []
    for ans in answers:
        correct_option = ans.question.options.filter(is_correct=True).first()
        answer_review.append({
            'question': ans.question,
            'selected': ans.selected_option,
            'correct_option': correct_option,
            'is_correct': ans.is_correct,
        })

    # Certificate
    certificate = getattr(attempt, 'certificate', None)

    context = {
        'quiz': quiz,
        'attempt': attempt,
        'total_marks': attempt.total_marks,
        'percentage': attempt.percentage,
        'grade': attempt.grade,
        'answer_review': answer_review,
        'certificate': certificate,
    }
    return render(request, 'quiz_result.html', context)


@login_required(login_url='student_login_view')
def download_report(request, quiz_id):
    if request.user.user_type != 'student':
        return redirect('student_login_view')

    quiz = get_object_or_404(Quiz.objects.select_related('subject'), id=quiz_id)
    attempt = QuizAttempt.objects.filter(
        student=request.user,
        quiz=quiz,
        is_completed=True,
    ).select_related('quiz__subject').prefetch_related(
        'answers__question__options',
        'answers__selected_option',
    ).order_by('-end_time', '-start_time').first()

    if not attempt:
        return redirect('stu_index')

    try:
        from xhtml2pdf import pisa
    except ImportError:
        return HttpResponse(
            "xhtml2pdf is not installed. Run: pip install xhtml2pdf",
            status=500,
        )

    total_questions = quiz.questions.count()
    correct_answers = attempt.answers.filter(is_correct=True).count()
    score = attempt.score
    total_marks = attempt.total_marks
    percentage = attempt.percentage
    progress_percent = max(0, min(100, float(percentage or 0)))
    attempted_on_dt = timezone.localtime(attempt.end_time or attempt.start_time)
    attempted_on = attempted_on_dt.strftime('%d %b %Y, %I:%M %p')
    generated_at = timezone.localtime()
    status_label = "PASS" if percentage >= 50 else "FAIL"
    status_color = "#16a34a" if percentage >= 50 else "#dc2626"

    student_name = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
    enrollment = request.user.enrollment_no or request.user.username
    subject_name = quiz.subject.name if quiz.subject else '-'

    question_summary = []
    answers = attempt.answers.select_related('question', 'selected_option').prefetch_related(
        'question__options'
    ).order_by('id')
    for idx, ans in enumerate(answers, start=1):
        correct_option = ans.question.options.filter(is_correct=True).first()
        question_summary.append({
            'no': idx,
            'question': ans.question.question_text,
            'selected': ans.selected_option.option_text if ans.selected_option else "Not Answered",
            'correct': correct_option.option_text if correct_option else "-",
            'is_correct': ans.is_correct,
        })

    logo_path = os.path.join(settings.BASE_DIR, 'quiz', 'static', 'images', 'logo.png')
    logo_uri = None
    if os.path.exists(logo_path):
        logo_uri = 'file:///' + logo_path.replace('\\', '/')

    safe_quiz_title = slugify(quiz.title) or f"quiz-{quiz.id}"
    safe_enrollment = slugify(str(enrollment)) or str(request.user.id)
    filename = f"report_{safe_quiz_title}_{safe_enrollment}.pdf"

    context = {
        'app_name': "Student Quiz Report",
        'student_name': student_name,
        'enrollment': enrollment,
        'subject': subject_name,
        'quiz_title': quiz.title,
        'attempted_on': attempted_on,
        'generated_at': generated_at.strftime('%d %b %Y, %I:%M %p'),
        'total_questions': total_questions,
        'correct_answers': correct_answers,
        'score': score,
        'total_marks': total_marks,
        'percentage': percentage,
        'progress_percent': progress_percent,
        'status_label': status_label,
        'status_color': status_color,
        'question_summary': question_summary,
        'logo_uri': logo_uri,
    }

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    html = render_to_string('report_template.html', context)
    pisa_status = pisa.CreatePDF(src=html, dest=response, encoding='utf-8')
    if pisa_status.err:
        return HttpResponse("Unable to generate PDF report at this time.", status=500)
    return response

@login_required(login_url='student_login_view')
def download_result(request, quiz_id):
    # Backward-compatible alias for older templates/URLs.
    return download_report(request, quiz_id)


# ============================================================
# CERTIFICATE
# ============================================================

@login_required(login_url='student_login_view')
def generate_certificate(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, student=request.user)

    if attempt.percentage < 40:
        if request.user.user_type == 'student':
            return redirect('quiz_result', quiz_id=attempt.quiz.id)
        return redirect('stu_index')

    cert, _ = Certificate.objects.get_or_create(attempt=attempt)

    context = {
        'cert': cert,
        'attempt': attempt,
        'student': request.user,
    }
    return render(request, 'certificate.html', context)
