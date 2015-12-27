from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class PasswordlessAuthBackend(ModelBackend):
    """
    Authenticate a user without having to provide a password
    """

    # TODO Perhaps add a token or something to make sure this backend isn't used accidentally
    def authenticate(self, username=None, email=None):
        """
        Authenticate by supplying the username or the email
        """
        try:
            if username:
                return User.objects.get(username=username)
            else:
                return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except(User.DoesNotExist):
            return None
