from django import forms
from .models import Quiz, Question, Option, Subject, CustomUser


class QuizForm(forms.ModelForm):
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    new_subject = forms.CharField(
        required=False,
        label='Or Add New Subject',
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Data Structures'})
    )
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-input'}),
        required=False
    )
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-input'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subject'].queryset = Subject.objects.all().order_by('name')
        self.fields['subject'].required = False
        self.order_fields([
            'title', 'subject', 'new_subject', 'description',
            'time_limit_minutes', 'max_questions', 'start_time', 'end_time', 'is_active'
        ])
        self.fields['max_questions'].label = 'Maximum Questions Allowed'
        self.fields['max_questions'].help_text = 'Set how many questions can be added to this quiz.'

    def clean(self):
        cleaned_data = super().clean()
        subject = cleaned_data.get('subject')
        new_subject = (cleaned_data.get('new_subject') or '').strip()

        if not subject and not new_subject:
            raise forms.ValidationError("Please select a subject or add a new one.")

        cleaned_data['new_subject'] = new_subject
        return cleaned_data

    def clean_max_questions(self):
        max_questions = self.cleaned_data.get('max_questions')
        if max_questions is None or max_questions < 1:
            raise forms.ValidationError("Maximum Questions Allowed must be at least 1.")
        return max_questions

    class Meta:
        model = Quiz
        fields = ['title', 'subject', 'description', 'time_limit_minutes', 'max_questions', 'start_time', 'end_time', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Enter Quiz Title'}),
            'subject': forms.Select(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Optional description...'}),
            'time_limit_minutes': forms.NumberInput(attrs={'class': 'form-input', 'min': 1}),
            'max_questions': forms.NumberInput(attrs={'class': 'form-input', 'min': 1}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['quiz', 'subject', 'question_text', 'question_type', 'difficulty', 'image', 'marks']
        widgets = {
            'quiz': forms.Select(attrs={'class': 'form-input'}),
            'subject': forms.Select(attrs={'class': 'form-input'}),
            'question_text': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Type the question here...'}),
            'question_type': forms.Select(attrs={'class': 'form-input'}),
            'difficulty': forms.Select(attrs={'class': 'form-input'}),
            'marks': forms.NumberInput(attrs={'class': 'form-input', 'min': 1}),
        }


class AddQuestionForm(forms.ModelForm):
    subject = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Python'})
    )
    option1 = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Option 1'})
    )
    option2 = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Option 2'})
    )
    option3 = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Option 3 (optional)'})
    )
    option4 = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Option 4 (optional)'})
    )
    correct_option = forms.ChoiceField(
        required=False,
        choices=(
            ('1', 'Option 1'),
            ('2', 'Option 2'),
            ('3', 'Option 3'),
            ('4', 'Option 4'),
        ),
        widget=forms.RadioSelect,
    )

    class Meta:
        model = Question
        fields = ['quiz', 'question_text', 'question_type', 'difficulty', 'image', 'marks']
        widgets = {
            'quiz': forms.Select(attrs={'class': 'form-input'}),
            'question_text': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Type the question here...'}),
            'question_type': forms.Select(attrs={'class': 'form-input'}),
            'difficulty': forms.Select(attrs={'class': 'form-input'}),
            'marks': forms.NumberInput(attrs={'class': 'form-input', 'min': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['quiz'].required = False
        self.order_fields([
            'quiz', 'subject', 'question_text', 'question_type', 'difficulty', 'image', 'marks',
            'option1', 'option2', 'option3', 'option4', 'correct_option',
        ])

    def clean(self):
        cleaned_data = super().clean()
        quiz = cleaned_data.get('quiz')
        subject_name = (cleaned_data.get('subject') or '').strip()
        question_type = cleaned_data.get('question_type')
        correct_option = (cleaned_data.get('correct_option') or '').strip()

        option1 = (cleaned_data.get('option1') or '').strip()
        option2 = (cleaned_data.get('option2') or '').strip()
        option3 = (cleaned_data.get('option3') or '').strip()
        option4 = (cleaned_data.get('option4') or '').strip()

        if not subject_name and quiz and quiz.subject:
            subject_name = quiz.subject.name

        if not subject_name:
            self.add_error('subject', 'Subject is required.')
        else:
            cleaned_data['subject'] = subject_name

        if question_type == 'TF':
            cleaned_data['option1'] = 'True'
            cleaned_data['option2'] = 'False'
            cleaned_data['option3'] = ''
            cleaned_data['option4'] = ''
            if correct_option not in ('1', '2'):
                self.add_error('correct_option', 'For True/False, select either True (Option 1) or False (Option 2).')
        else:
            provided_options = [
                (1, option1),
                (2, option2),
                (3, option3),
                (4, option4),
            ]
            filled_options = [(idx, text) for idx, text in provided_options if text]
            if len(filled_options) < 2:
                self.add_error('option2', 'For multiple choice, add at least 2 options.')

            if correct_option not in ('1', '2', '3', '4'):
                self.add_error('correct_option', 'Please select the correct answer.')
            else:
                selected_index = int(correct_option)
                filled_indexes = {idx for idx, _ in filled_options}
                if selected_index not in filled_indexes:
                    self.add_error('correct_option', 'Correct answer must match a filled option.')

        return cleaned_data

    def save(self, commit=True):
        question = super().save(commit=False)
        subject_name = self.cleaned_data.get('subject', '').strip()
        subject = Subject.objects.filter(name__iexact=subject_name).first()
        if subject is None:
            subject = Subject.objects.create(name=subject_name)
        question.subject = subject

        if commit:
            question.save()
        else:
            return question

        question_type = self.cleaned_data.get('question_type')
        correct_option = int(self.cleaned_data.get('correct_option'))

        if question_type == 'TF':
            options_payload = [(1, 'True'), (2, 'False')]
        else:
            options_payload = [
                (1, (self.cleaned_data.get('option1') or '').strip()),
                (2, (self.cleaned_data.get('option2') or '').strip()),
                (3, (self.cleaned_data.get('option3') or '').strip()),
                (4, (self.cleaned_data.get('option4') or '').strip()),
            ]
            options_payload = [(idx, text) for idx, text in options_payload if text]

        Option.objects.bulk_create([
            Option(
                question=question,
                option_text=option_text,
                is_correct=(idx == correct_option),
            )
            for idx, option_text in options_payload
        ])
        return question


class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['option_text', 'is_correct']
        widgets = {
            'option_text': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Enter option text'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email', 'enrollment_no', 'phone_number', 'year', 'semester', 'section', 'roll_number',
            'branch', 'department', 'proctor', 'admission_year', 'cgpa', 'attendance', 'address', 'date_of_birth', 'gender', 'profile_photo'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'enrollment_no': forms.TextInput(attrs={'class': 'form-input'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-input'}),
            'year': forms.TextInput(attrs={'class': 'form-input'}),
            'semester': forms.NumberInput(attrs={'class': 'form-input', 'min': 1}),
            'section': forms.TextInput(attrs={'class': 'form-input'}),
            'roll_number': forms.TextInput(attrs={'class': 'form-input'}),
            'branch': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Computer Science'}),
            'department': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. CSE'}),
            'proctor': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Prof. Smith'}),
            'admission_year': forms.NumberInput(attrs={'class': 'form-input', 'min': 1900, 'max': 2100}),
            'cgpa': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0', 'max': '10'}),
            'attendance': forms.NumberInput(attrs={'class': 'form-input', 'min': '0', 'max': '100'}),
            'address': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-input'}),
            'profile_photo': forms.ClearableFileInput(attrs={'class': 'form-input'}),
        }


class AdminStudentCreateForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Set a secure password'}),
        strip=False,
    )

    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email', 'enrollment_no', 'phone_number', 'year',
            'semester', 'section', 'roll_number', 'branch', 'department', 'proctor',
            'admission_year', 'cgpa', 'attendance', 'address', 'date_of_birth', 'profile_photo',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. John'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Doe'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'student@example.com'}),
            'enrollment_no': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. EN21CS001'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 9876543210'}),
            'year': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 2022'}),
            'semester': forms.NumberInput(attrs={'class': 'form-input', 'min': 1}),
            'section': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. A'}),
            'roll_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 22bt04147'}),
            'branch': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Computer Science'}),
            'department': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. CSE'}),
            'proctor': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Prof. Sharma'}),
            'admission_year': forms.NumberInput(attrs={'class': 'form-input', 'min': 1900, 'max': 2100}),
            'cgpa': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0', 'max': '10'}),
            'attendance': forms.NumberInput(attrs={'class': 'form-input', 'min': '0', 'max': '100'}),
            'address': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'profile_photo': forms.ClearableFileInput(attrs={'class': 'form-input'}),
        }
        labels = {
            'enrollment_no': 'Enrollment No',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['email'].required = True
        self.fields['enrollment_no'].required = True
        self.fields['attendance'].required = False
        self.fields['cgpa'].required = False
        self.fields['attendance'].initial = 0
        self.fields['cgpa'].initial = 0.0

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip()
        if not email:
            raise forms.ValidationError("Email is required.")
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean_enrollment_no(self):
        enrollment_no = (self.cleaned_data.get('enrollment_no') or '').strip()
        if not enrollment_no:
            raise forms.ValidationError("Enrollment number is required.")
        if CustomUser.objects.filter(enrollment_no__iexact=enrollment_no).exists():
            raise forms.ValidationError("This enrollment number is already registered.")
        return enrollment_no

    def save(self, commit=True):
        student = super().save(commit=False)
        enrollment_no = self.cleaned_data['enrollment_no']
        student.username = enrollment_no
        student.user_type = 'student'
        student.set_password(self.cleaned_data['password'])
        if commit:
            student.save()
        return student


class AdminStudentEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'username', 'email', 'enrollment_no',
            'phone_number', 'year', 'semester', 'section', 'roll_number', 'branch', 'department', 'proctor',
            'admission_year', 'cgpa', 'attendance', 'address', 'date_of_birth', 'gender', 'profile_photo',
            'review', 'can_edit_profile'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'username': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'enrollment_no': forms.TextInput(attrs={'class': 'form-input'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-input'}),
            'year': forms.TextInput(attrs={'class': 'form-input'}),
            'semester': forms.NumberInput(attrs={'class': 'form-input', 'min': 1}),
            'section': forms.TextInput(attrs={'class': 'form-input'}),
            'roll_number': forms.TextInput(attrs={'class': 'form-input'}),
            'branch': forms.TextInput(attrs={'class': 'form-input'}),
            'department': forms.TextInput(attrs={'class': 'form-input'}),
            'proctor': forms.TextInput(attrs={'class': 'form-input'}),
            'admission_year': forms.NumberInput(attrs={'class': 'form-input', 'min': 1900, 'max': 2100}),
            'cgpa': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0', 'max': '10'}),
            'attendance': forms.NumberInput(attrs={'class': 'form-input', 'min': '0', 'max': '100'}),
            'address': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-input'}),
            'profile_photo': forms.ClearableFileInput(attrs={'class': 'form-input'}),
            'review': forms.NumberInput(attrs={'class': 'form-input', 'min': '0'}),
            'can_edit_profile': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        label='Registered Email Address',
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your registered email',
            'required': 'required'
        })
    )


class OTPVerificationForm(forms.Form):
    otp = forms.CharField(
        label='OTP',
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter 6-digit OTP',
            'type': 'text',
            'inputmode': 'numeric',
        })
    )
    new_password = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '••••••••',
            'required': 'required'
        })
    )
    confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '••••••••',
            'required': 'required'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        otp = cleaned_data.get('otp')

        if otp and not otp.isdigit():
            self.add_error('otp', 'OTP must contain only digits.')

        if new_password and confirm_password:
            if new_password != confirm_password:
                self.add_error('confirm_password', 'Passwords do not match.')
            if len(new_password) < 8:
                self.add_error('new_password', 'Password must be at least 8 characters long.')

        return cleaned_data
