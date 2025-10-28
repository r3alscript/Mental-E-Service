from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("select-role/", views.select_role, name="select_role"),
    path("register-client/", views.register_client, name="register_client"),
    path("register-psychologist/personal/", views.register_psychologist_personal, name="register_psychologist_personal"),
    path("register-psychologist/professional/", views.register_psychologist_professional, name="register_psychologist_professional"),
    path("guest-login/", views.guest_login, name="guest_login"),
    path("register-success/", views.register_success, name="register_success"),
]
