from django.shortcuts import render, get_object_or_404, redirect
from authorization.models import Psychologist
from booking.models import Booking
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json
from django.conf import settings
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.contrib import messages

User = get_user_model()
@login_required
def psychologists_list_api(request):
    psychologists = Psychologist.objects.select_related("user").exclude(work_time="")

    result = []
    for psycho in psychologists:
        user = psycho.user

        if user.avatar and user.avatar.name:
            avatar_url = request.build_absolute_uri(user.avatar.url)
        else:
            avatar_url = request.build_absolute_uri(
                settings.MEDIA_URL + "avatars/default_avatar.png"
            )

        result.append({
            "id": psycho.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "experience": psycho.experience,
            "price": float(psycho.price),
            "language": psycho.language,
            "cancel_policy": psycho.cancel_policy,
            "rating": 5.0,
            "avatar_url": avatar_url,
        })

    return JsonResponse({"psychologists": result})

@login_required
def psychologists_list(request):
    psychologists = Psychologist.objects.select_related("user").exclude(work_time="")

    result = []
    for psycho in psychologists:
        user = psycho.user

        if user.avatar and user.avatar.name:
            avatar_url = user.avatar.url
        else:
            avatar_url = settings.MEDIA_URL + "avatars/default_avatar.png"

        result.append({
            "id": psycho.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "experience": psycho.experience,
            "price": float(psycho.price),
            "language": psycho.language,
            "cancel_policy": psycho.cancel_policy,
            "rating": 5.0,
            "avatar_url": avatar_url,
            "work_time": psycho.work_time
        })

    return render(request, "booking/psychologists_list.html", {
        "psychologists_json": json.dumps(result)
    })


@login_required
def booking_page(request):
    bookings = Booking.objects.filter(
        client=request.user,
        is_expired=False
    ).order_by("date", "time")

    return render(request, "booking/booking_page.html", {
        "bookings": bookings
    })

@login_required
def create_booking(request, psychologist_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    date_str = request.POST.get("date")
    time_str = request.POST.get("time")

    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        time_obj = datetime.strptime(time_str, "%H:%M").time()
    except Exception:
        return JsonResponse({"error": "Invalid date/time format"}, status=400)

    psychologist = get_object_or_404(Psychologist, id=psychologist_id)

    if Booking.objects.filter(
        psychologist=psychologist,
        date=date_obj,
        time=time_obj
    ).exists():
        return JsonResponse({"message": "exists"})

    Booking.objects.create(
        client=request.user,
        psychologist=psychologist,
        date=date_obj,
        time=time_obj,
        status="pending"
    )

    return JsonResponse({"message": "ok"})

@login_required
def get_available_times(request, psychologist_id):
    date = request.GET.get("date")
    if not date:
        return JsonResponse({"error": "date required"}, status=400)

    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
    except:
        return JsonResponse({"free_times": []})

    psycho = get_object_or_404(Psychologist, id=psychologist_id)

    if not psycho.work_time:
        return JsonResponse({"free_times": []})

    work_time = psycho.work_time.replace("–", "-").replace("—", "-")
    parts = work_time.split("-")

    if len(parts) != 2:
        return JsonResponse({"free_times": []})

    start_str = parts[0].strip()
    end_str = parts[1].strip()

    try:
        start = datetime.strptime(start_str, "%H:%M")
        end = datetime.strptime(end_str, "%H:%M")
    except ValueError:
        return JsonResponse({"free_times": []})

    times = []
    t = start
    while t < end:
        times.append(t.strftime("%H:%M"))
        t += timedelta(hours=1)

    booked = Booking.objects.filter(
        psychologist=psycho,
        date=date_obj
    ).values_list("time", flat=True)

    booked = {t.strftime("%H:%M") for t in booked}

    free = [t for t in times if t not in booked]

    return JsonResponse({"free_times": free})

@login_required
def my_bookings_client(request):
    now = datetime.now()

    bookings = Booking.objects.filter(
        client=request.user,
        status="pending"
    ) | Booking.objects.filter(
        client=request.user,
        status="approved"
    )

    bookings = bookings.order_by("date", "time")

    for b in bookings:
        booking_dt = datetime.combine(b.date, b.time)
        if booking_dt < now and b.status == "approved":
            b.status = "completed"
            b.save()

    bookings = Booking.objects.filter(
        client=request.user,
        status__in=["pending", "approved"]
    ).order_by("date", "time")

    return render(request, "booking/my_bookings_client.html", {
        "bookings": bookings
    })

@login_required
def my_bookings_psychologist(request):
    try:
        psycho = Psychologist.objects.get(user=request.user)
    except Psychologist.DoesNotExist:
        return redirect("/")

    pending = Booking.objects.filter(
        psychologist=psycho,
        status="pending"
    ).order_by("date", "time")

    approved = Booking.objects.filter(
        psychologist=psycho,
        status="approved"
    ).order_by("date", "time")

    return render(request, "booking/my_bookings_psychologist.html", {
        "pending": pending,
        "approved": approved
    })

@login_required
def approve_booking(request, booking_id):
    b = get_object_or_404(Booking, id=booking_id)
    b.status = "approved"
    b.save()
    return JsonResponse({"ok": True})


@login_required
def reject_booking(request, booking_id):
    b = get_object_or_404(Booking, id=booking_id)
    b.status = "rejected"
    b.save()
    return JsonResponse({"ok": True})


@login_required
def cancel_booking(request, booking_id):
    b = get_object_or_404(Booking, id=booking_id)

    if b.client == request.user:
        b.status = "canceled"
        b.save()

    return JsonResponse({"ok": True})

@login_required
def booking_router(request):
    user = request.user

    if hasattr(user, "psychologist_profile"):
        return redirect("my_bookings_psychologist")

    return redirect("my_bookings_client")

@login_required
def booking_history(request):
    if hasattr(request.user, "psychologist_profile"):
        psycho = request.user.psychologist_profile
        history = Booking.objects.filter(
            psychologist=psycho
        ).exclude(status="pending")
    else:
        history = Booking.objects.filter(
            client=request.user
        ).exclude(status="pending")

    history = history.order_by("-date", "-time")

    for b in history:
        b.save()

    return render(request, "booking/booking_history.html", {
        "history": history
    })