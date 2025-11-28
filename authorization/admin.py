from django.contrib import admin
from .models import User, Client, Psychologist


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "first_name", "last_name", "role", "created_at")
    list_filter = ("role",)
    search_fields = ("username", "email", "first_name", "last_name")


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("user",)
    search_fields = ("user__email",)


@admin.register(Psychologist)
class PsychologistAdmin(admin.ModelAdmin):
    list_display = ("user", "specialization", "language")
    search_fields = ("user__email", "specialization", "language")