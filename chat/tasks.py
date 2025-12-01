from celery import shared_task
from django.contrib.auth import get_user_model
from .models import Message, UnreadStatus

User = get_user_model()

@shared_task
def notify_unread(message_id):
    msg = Message.objects.select_related(
        "dialog__client__user",
        "dialog__psychologist__user",
        "sender"
    ).get(id=message_id)

    dialog = msg.dialog
    sender = msg.sender

    if sender == dialog.client.user:
        recipient = dialog.psychologist.user
    else:
        recipient = dialog.client.user

    UnreadStatus.objects.update_or_create(
        user=recipient,
        defaults={"has_unread": True},
    )
