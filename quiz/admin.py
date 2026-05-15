from django.contrib import admin
from .models import CustomUser, Subject, Quiz, Question, Option, QuizAttempt, StudentAnswer, ContactQuery


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'user_type',
        'enrollment_no', 'phone_number', 'branch', 'department', 'semester', 'year', 'section',
        'can_edit_profile'
    )
    list_filter = ('user_type', 'branch', 'department', 'gender', 'can_edit_profile')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'enrollment_no', 'roll_number')
    ordering = ('username',)
    fieldsets = (
        ('Login Info', {'fields': ('username', 'password', 'user_type')}),
        ('Personal', {
            'fields': (
                'first_name', 'last_name', 'email', 'phone_number', 'date_of_birth', 'gender', 'profile_photo', 'address'
            )
        }),
        ('Academic', {
            'fields': (
                'enrollment_no', 'roll_number', 'branch', 'department', 'year', 'semester', 'section', 'proctor', 'admission_year', 'cgpa', 'attendance', 'review'
            )
        }),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'can_edit_profile')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )


admin.site.register(Subject)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Option)
admin.site.register(QuizAttempt)
admin.site.register(StudentAnswer)
admin.site.register(ContactQuery)