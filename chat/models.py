from django.db import models
from django.conf import settings
from authorization.models import Client, Psychologist  

User = settings.AUTH_USER_MODEL


class Dialog(models.Model):
    client = models.ForeignKey(User, related_name="client_dialogs", on_delete=models.CASCADE)
    psychologist = models.ForeignKey(User, related_name="psychologist_dialogs", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("client", "psychologist")

    def __str__(self):
        return f"Dialog {self.id} ({self.client.email} - {self.psychologist.email})"


class Message(models.Model):
    dialog = models.ForeignKey(Dialog, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.sender} -> Dialog {self.dialog_id}: {self.text[:30]}"
    
class UnreadStatus(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    has_unread = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user",)
