from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash
import json
import os
from json import JSONDecodeError
from decimal import Decimal
from datetime import datetime
import re


@login_required
def client_profile_view(request):
    user = request.user
    profile = getattr(user, "client_profile", None)

    return render(request, 'profiles/client_profile.html', {
        "user": user,
        "profile": profile
    })


@login_required
def psychologist_profile_view(request):
    user = request.user
    profile = getattr(user, "psychologist_profile", None)

    return render(request, "profiles/psychologist_profile.html", {
        "user": user,
        "profile": profile
    })

@login_required
def delete_account_view(request):
    request.user.delete()
    return redirect("auth/login")
  
@login_required
def change_password_ajax(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=400)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    old_password = data.get("old_password")
    new_password = data.get("new_password")

    if not old_password or not new_password:
        return JsonResponse({"error": "Заповніть всі поля"}, status=400)

    user = request.user

    if not user.check_password(old_password):
        return JsonResponse({"error": "Невірний поточний пароль"}, status=400)

    user.set_password(new_password)
    user.save()
    update_session_auth_hash(request, user)

    return JsonResponse({"success": True})

@login_required
def profile_router(request):
    if request.user.role == "client":
        return redirect("client_profile")
    if request.user.role == "psychologist":
        return redirect("psychologist_profile")
    return redirect("login")


@login_required
def update_personal_ajax(request):
    print("RAW BODY:", request.body)

    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=400)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    user = request.user
    allowed = {"first_name", "last_name", "patronymic", "phone", "email", "birth_date"}

    for field, value in data.items():
        if field not in allowed:
            continue

        if field == "birth_date" and value:
            try:
                user.birth_date = datetime.strptime(value, "%Y-%m-%d").date()
                continue
            except ValueError:
                return JsonResponse({"error": "Невірний формат дати (YYYY-MM-DD)"}, status=400)

        setattr(user, field, value)

    user.save()
    return JsonResponse({"success": True})


@login_required
def update_workspace_ajax(request):
    print("RAW BODY:", request.body)
    if request.user.role != "psychologist":
        return JsonResponse({"error": "Forbidden"}, status=403)

    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=400)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    profile = request.user.psychologist_profile
    allowed = {"specialization", "language", "work_time", "experience", "price", "cancel_policy", "about"}

    for field, value in data.items():
        if field not in allowed:
            continue

        if field == "work_time":
            pattern = r"^\d{2}:\d{2}\s*-\s*\d{2}:\d{2}$"
            if not re.match(pattern, value):
                return JsonResponse({"error": "Некоректний формат робочого графіка (приклад: 08:00 - 22:00)"}, status=400)
            profile.work_time = value
            continue

        if field == "experience":
            try:
                profile.experience = int(value)
                continue
            except ValueError:
                return JsonResponse({"error": "Стаж має бути числом"}, status=400)

        if field == "price":
            try:
                profile.price = Decimal(value)
                continue
            except Exception:
                return JsonResponse({"error": "Вартість має бути числом"}, status=400)

        setattr(profile, field, value)

    profile.save()
    return JsonResponse({"success": True})


@login_required
def upload_avatar_ajax(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=400)

    file = request.FILES.get("avatar")
    if not file:
        return JsonResponse({"error": "Файл не отримано"}, status=400)

    user = request.user

    if user.avatar and user.avatar.name != "/media/avatars/default_avatar.png":
        old_path = user.avatar.path
        if os.path.exists(old_path):
            os.remove(old_path)

    user.avatar = file
    user.save()  

    return JsonResponse({
        "success": True,
        "url": user.avatar.url
    })

    
  