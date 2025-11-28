from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import time

def avatar_upload_path(instance, filename):
    ext = filename.split('.')[-1]

    if not instance.id:
        instance.save()   

    filename = f"avatar_{int(time.time())}.{ext}"
    return f"avatars/{instance.id}/{filename}"

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
    phone = models.CharField(max_length=15, blank=False)
    patronymic = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    document_type = models.CharField(max_length=50, blank=True)
    document_number = models.CharField(max_length=15, blank=True)
    avatar = models.ImageField(upload_to=avatar_upload_path, default="profiles/media/default_avatar.png")

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
    about = models.TextField(blank=True)
    language = models.CharField(max_length=100, blank=True)
    work_time = models.CharField(max_length=50, blank=True)
    experience = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)


    cancel_policy = models.CharField(
        max_length=255,
        choices=[
            ("24_hours", "За 24 години"),
            ("12_hours", "За 12 годин"),
            ("6_hours", "За 6 годин"),
        ],
        default="24_hours"
    )

    consultation_format = models.CharField(
        max_length=50,
        choices=[
            ("online", "Онлайн"),
            ("offline", "Офлайн"),
            ("both", "Онлайн та офлайн")
        ],
        default="online"
    )

    def __str__(self):
        return f"Психолог: {self.user.email}"
