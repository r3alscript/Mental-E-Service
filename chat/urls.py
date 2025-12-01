from django.urls import path
from . import views

app_name = "chat"

urlpatterns = [
    path("", views.chat_list_view, name="list"),                
    path("<int:dialog_id>/", views.dialog_view, name="dialog"), 
    path("api/unread/", views.check_unread, name="check_unread"),
    path("start/<int:psychologist_id>/", views.start_dialog, name="start"),
]
