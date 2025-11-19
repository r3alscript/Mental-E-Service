from django.urls import path
from . import views

urlpatterns = [
    path('psychologists/', views.psychologists_list, name='psychologists_list'),
    path('booking/', views.booking_page, name='booking_page'), 
    path('calendar/', views.calendar_page, name='calendar_page'),
]