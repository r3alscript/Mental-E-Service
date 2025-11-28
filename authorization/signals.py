from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Client, Psychologist

@receiver(post_save, sender=User)
def create_role_profile(sender, instance, created, **kwargs):
    if not created:
        return

    if instance.role == "client":
        Client.objects.create(user=instance)

    if instance.role == "psychologist":
        Psychologist.objects.create(user=instance)
