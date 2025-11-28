from django.contrib.auth.backends import ModelBackend
from .models import User

class PhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username:
            return None

        phone = username.replace(" ", "").replace("-", "")

        if phone.startswith("+380"):
            phone = phone[4:]
        elif phone.startswith("380"):
            phone = phone[3:]
        elif phone.startswith("0"):
            phone = phone[1:]


        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            return user

        return None
