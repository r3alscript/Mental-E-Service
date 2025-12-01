from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Dialog, Message, UnreadStatus
from authorization.models import Psychologist
from django.http import JsonResponse, HttpResponse
from django.conf import settings


@login_required
def chat_list_view(request):
    user = request.user

    if user.role == "client":
        dialogs = Dialog.objects.filter(client=user)
    else:
        dialogs = Dialog.objects.filter(psychologist=user)

    dialog_list = []

    for d in dialogs:
        other_user = d.psychologist if d.client == user else d.client
        last_msg = d.messages.order_by("-created_at").first()

        unread_count = d.messages.filter(
            is_read=False,
            sender=other_user
        ).count()

        dialog_list.append({
            "dialog": d,
            "other_user": other_user,
            "last_msg": last_msg,
            "unread_count": unread_count
        })

    return render(request, "chat/chat_list.html", {
        "dialogs": dialog_list,
        "has_dialogs": len(dialog_list) > 0
    })
    
@login_required
def dialog_view(request, dialog_id):
    dialog = get_object_or_404(Dialog, id=dialog_id)

    if dialog.client == request.user:
        other = dialog.psychologist
    else:
        other = dialog.client

    messages = dialog.messages.order_by("created_at")

    dialog.messages.exclude(sender=request.user).update(is_read=True)

    if request.user.avatar and "default_avatar" not in request.user.avatar.name:
        my_avatar = request.user.avatar.url
    else:
        my_avatar = "/media/avatars/default_avatar.png"

    if other.avatar and "default_avatar" not in other.avatar.name:
        other_avatar = other.avatar.url
    else:
        other_avatar = "/media/avatars/default_avatar.png"

    return render(request, "chat/dialog.html", {
        "dialog": dialog,
        "messages": messages,
        "my_user": request.user,
        "other": other,
        "my_avatar": my_avatar,
        "other_avatar": other_avatar,
    })

@login_required
def check_unread(request):
    status, _ = UnreadStatus.objects.get_or_create(user=request.user)
    return JsonResponse({"has_unread": status.has_unread})

@login_required
def start_dialog(request, psychologist_id):
    user = request.user

    if user.role != "client":
        return HttpResponse("Створити чат може лише клієнт", status=403)

    psycho = get_object_or_404(Psychologist, id=psychologist_id)

    dialog, created = Dialog.objects.get_or_create(
        client=user,
        psychologist=psycho.user
    )

    return redirect("chat:dialog", dialog.id)


