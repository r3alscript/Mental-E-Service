from django.urls import path
from .views import (
    profile_router,
    client_profile_view,
    psychologist_profile_view,
    delete_account_view,
    change_password_ajax,
    update_personal_ajax,      
    update_workspace_ajax,
    upload_avatar_ajax     
)

urlpatterns = [
    path("", profile_router, name="profile_router"),
    path("client/", client_profile_view, name="client_profile"),
    path("psychologist/", psychologist_profile_view, name="psychologist_profile"),
    path("delete/", delete_account_view, name="delete_account"),
    path("change-password/", change_password_ajax, name="change_password"),
    path("update_personal/", update_personal_ajax, name="update_personal"),
    path("update_workspace/", update_workspace_ajax, name="update_workspace"),
    path("upload_avatar/", upload_avatar_ajax, name="upload_avatar"),
]
