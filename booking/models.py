from django.db import models
from authorization.models import User, Psychologist

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Очікує підтвердження'),
        ('confirmed', 'Підтверджено'),
        ('cancelled', 'Скасовано'),
        ('completed', 'Завершено'),
    ]
    
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    psychologist = models.ForeignKey(Psychologist, on_delete=models.CASCADE, related_name='bookings')
    date = models.DateField()
    time = models.TimeField()
    duration = models.IntegerField(default=60)  # длительность в минутах
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.client} - {self.psychologist} - {self.date} {self.time}"