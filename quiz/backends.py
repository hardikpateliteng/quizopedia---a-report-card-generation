from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # We can receive `email` or `enroll_no` as `username` depending on the view
        # or we accept explicitly email and enrollment_no kwargs.
        
        email = kwargs.get('email')
        enrollment_no = kwargs.get('enrollment_no')
        
        if email:
            try:
                user = UserModel.objects.get(email=email)
            except UserModel.DoesNotExist:
                return None
        elif enrollment_no:
            try:
                user = UserModel.objects.get(enrollment_no=enrollment_no)
            except UserModel.DoesNotExist:
                return None
        elif username:
            # Fallback for generic username logins
            try:
                user = UserModel.objects.get(username=username)
            except UserModel.DoesNotExist:
                return None
        else:
            return None
            
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
