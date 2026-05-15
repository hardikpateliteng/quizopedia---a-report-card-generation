from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.home_view, name='home'),

    # Admin Auth
    path('admin_login/', views.LoginUserView, name='sign1'),
    path('adlogout/', views.logout_admin, name='admlogout'),

    # Admin Dashboard
    path('index/', views.index, name='index1'),
    path('analytics/', views.admin_analytics, name='admin_analytics'),

    # Admin Student Management
    path('addstudent/', views.add_student, name='addstudent'),
    path('student/<int:student_id>/detail/', views.admin_student_detail, name='admin_student_detail'),
    path('student/<int:student_id>/edit/', views.edit_student_profile, name='edit_student_profile'),
    path('student/<int:student_id>/toggle-profile-edit/', views.toggle_student_profile_permission, name='toggle_student_profile_permission'),
    path('student/<int:student_id>/delete/', views.delete_student, name='delete_student'),
    path('student-data/', views.student_data, name='student_data'),
    path('studentreport/', views.student_report, name='studentreport1'),
    path('download_report/<int:student_id>/', views.download_student_report_csv, name='download_student_report_csv'),

    # Admin Quiz Management
    path('createtest/', views.create_quiz, name='create1'),
    path('viewquiz/', views.view_quizzes, name='viewquiz'),
    path('quiz/<int:quiz_id>/edit/', views.edit_quiz, name='edit_quiz'),
    path('quiz/<int:quiz_id>/delete/', views.delete_quiz, name='delete_quiz'),
    path('quiz/<int:quiz_id>/toggle/', views.toggle_quiz, name='toggle_quiz'),

    # Admin Question Management
    path('viewquestion/', views.view_questions, name='viewquestion'),
    path('addquestion/', views.add_question, name='addquestion'),
    path('addoption/<int:question_id>/', views.add_option, name='addoption'),
    path('question/<int:question_id>/delete/', views.delete_question, name='delete_question'),

    # Admin Reports & Attendance
    path('attendance/', views.view_attendance, name='view_attendance'),
    path('leaderboard/', views.global_leaderboard, name='leaderboard'),

    # Student Auth
    path('login/', views.student_login_view, name='student_login_view'),
    path('stu_logout/', views.student_logout_view, name='student_logout_view'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password_view'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp_view'),

    # Student Pages
    path('stu_index/', views.student_dashboard, name='stu_index'),
    path('stu_profile/', views.student_profile, name='stu_profile'),
    path('quiz_history/', views.quiz_history, name='quiz_history'),
    path('take_quiz/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    path('quiz_result/<int:quiz_id>/', views.quiz_result, name='quiz_result'),
    path('download-report/<int:quiz_id>/', views.download_report, name='download_report'),
    path('download-result/<int:quiz_id>/', views.download_result, name='download_result'),
    path('certificate/<int:attempt_id>/', views.generate_certificate, name='generate_certificate'),
]
