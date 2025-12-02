from . import views
from django.urls import path

urlpatterns = [
    path("hotlines/", views.hotlines_page, name="hotlines")
]
