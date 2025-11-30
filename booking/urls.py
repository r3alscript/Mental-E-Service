from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('psychologists/', views.psychologists_list, name='psychologists_list'),
    path('psychologists/api/', views.psychologists_list_api, name='psychologists_list_api'),
    path('booking/', views.booking_page, name='booking_page'),
    path('free-times/<int:psychologist_id>/', views.get_available_times),
    path('create/<int:psychologist_id>/', views.create_booking),
    path('my/', views.my_bookings_client, name='my_bookings_client'),
    path('manage/', views.my_bookings_psychologist, name='my_bookings_psychologist'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('approve/<int:booking_id>/', views.approve_booking, name='approve_booking'),
    path('reject/<int:booking_id>/', views.reject_booking, name='reject_booking'),
    path('router/', views.booking_router, name='booking_router'),
    path("history/", views.booking_history, name="booking_history"),
] 