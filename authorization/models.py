from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    ROLE_CHOICES = [
        ('client', 'Клієнт'),
        ('psychologist', 'Психолог'),
        ('guest', 'Гість'),
        ('admin', 'Адміністратор'),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='guest')
    created_at = models.DateTimeField(default=timezone.now)
    phone = models.CharField(max_length=15, blank=True)
    patronymic = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    document_type = models.CharField(max_length=50, blank=True)
    document_number = models.CharField(max_length=15, blank=True)
    tz = models.CharField(max_length=50, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = 'admin'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')

    def __str__(self):
        return f"Клієнт: {self.user.email}"


class Psychologist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='psychologist_profile')
    specialization = models.CharField(max_length=100, blank=True)
    language = models.CharField(max_length=50, blank=True)
    tz = models.CharField(max_length=50, blank=True)
    about = models.TextField(blank=True)
    policy = models.TextField(blank=True)
    format = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"Психолог: {self.user.email}"
