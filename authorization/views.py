from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import User, Client, Psychologist
from .forms import PsychologistPersonalForm, PsychologistWorkForm, ClientRegisterForm
import uuid

def select_role(request):
    return render(request, "auth/select_role.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        phone = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        clean = phone.replace(" ", "").replace("-", "")
        if clean.startswith("+380"):
            clean = clean[4:]
        elif clean.startswith("380"):
            clean = clean[3:]
        elif clean.startswith("0"):
            clean = clean[1:]

        user = authenticate(request, username=clean, password=password)

        if user:
            login(request, user)
            return redirect("profile_router")
        else:
            messages.error(request, "Невірний номер телефону або пароль.")

    return render(request, "auth/login.html")


def logout_view(request):
    logout(request)
    return redirect("/auth/login/")


def guest_login(request):
    username = f"guest_{uuid.uuid4().hex[:8]}"
    email = f"{username}@temporary.local"
    guest = User.objects.create_user(
        username=username,
        email=email,
        first_name="Guest",
        last_name="Anonymous",
        role="guest",
        password=None
    )
    login(request, guest, backend="django.contrib.auth.backends.ModelBackend")
    return render(request, "auth/guest_login.html", {"guest_username": username})


def register_client(request):
    if request.method == "POST":
        form = ClientRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            request.session["auto_login_user_id"] = user.id

            return redirect("register_success")

    else:
        form = ClientRegisterForm()

    return render(request, "auth/register_client.html", {"form": form})


def register_psychologist_personal(request):
    if request.method == "POST":
        form = PsychologistPersonalForm(request.POST)
        if form.is_valid():
            user = form.save()

            request.session["psychologist_user_id"] = user.id

            messages.success(request, "Особисті дані збережено!")
            return redirect("register_psychologist_professional")
        else:
            messages.error(request, "Будь ласка, виправте помилки у формі.")
    else:
        form = PsychologistPersonalForm()

    return render(request, "auth/register_psychologist_personal.html", {"form": form})



def register_psychologist_professional(request):
    user_id = request.session.get("psychologist_user_id")
    if not user_id:
        return redirect("register_psychologist_personal")

    user = User.objects.filter(id=user_id).first()
    if not user:
        messages.error(request, "Користувача не знайдено.")
        return redirect("register_psychologist_personal")

    if request.method == "POST":
        form = PsychologistWorkForm(request.POST)

        if form.is_valid():
            profile, created = Psychologist.objects.get_or_create(user=user)

            data = form.cleaned_data
            profile.specialization = data["specialization"]
            profile.language = data["language"]
            profile.about = data["about"]
            profile.cancel_policy = data["cancel_policy"]
            profile.consultation_format = data["consultation_format"]
            profile.save()
            request.session.pop("psychologist_user_id", None)
            request.session["auto_login_user_id"] = user.id

            messages.success(request, "Психолога успішно зареєстровано!")
            return redirect("register_success")

        else:
            messages.error(request, "Будь ласка, перевірте введені дані.")
    else:
        form = PsychologistWorkForm()

    return render(request, "auth/register_psychologist_professional.html", {"form": form})



def register_success(request):
    user_id = request.session.get("auto_login_user_id")

    if user_id:
        user = User.objects.get(id=user_id)
        user.backend = "django.contrib.auth.backends.ModelBackend"
        login(request, user)
        del request.session["auto_login_user_id"]

    return render(request, "auth/register_success.html", {
        "role": request.user.role if request.user.is_authenticated else None
    })