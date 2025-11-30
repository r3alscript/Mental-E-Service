from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "psychologist", "date", "time", "status", "is_expired", "created_at")
    list_filter = ("status", "date", "psychologist")
    search_fields = ("client__email", "psychologist__email")
