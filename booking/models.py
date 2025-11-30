from django.db import models
from django.conf import settings
from datetime import datetime
from authorization.models import Psychologist

class Booking(models.Model):
    STATUS_CHOICES = [
        ("pending", "В процесі"),
        ("approved", "Підтверджено"),
        ("rejected", "Відхилено"),
        ("canceled", "Скасовано"),
        ("completed", "Завершено"),
    ]

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_bookings"
    )

    psychologist = models.ForeignKey(
        Psychologist,
        on_delete=models.CASCADE,
        related_name="bookings"
    )

    date = models.DateField()
    time = models.TimeField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    is_expired = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("psychologist", "date", "time")
        ordering = ["-date", "-time"]

    def __str__(self):
        return f"{self.client} → {self.psychologist.user.email} ({self.date} {self.time})"

    def check_expired(self):
        now = datetime.now()
        booking_dt = datetime.combine(self.date, self.time)
        self.is_expired = booking_dt < now

        if booking_dt < now and self.status == "approved":
            self.status = "completed"

        return self.is_expired

    def save(self, *args, **kwargs):
        self.check_expired()
        super().save(*args, **kwargs)
