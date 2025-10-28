from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import User, Psychologist
from .forms import PsychologistPersonalForm, PsychologistWorkForm
from datetime import date
import uuid


def select_role(request):
    return render(request, "auth/select_role.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("/")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if not user:
            try:
                user_obj = User.objects.get(email=username)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None
        if user:
            login(request, user)
            messages.success(request, f"Вітаємо, {user.first_name}!")
            return redirect("/")
        else:
            messages.error(request, "Невірний логін або пароль.")
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
        first_name="Anonymous",
        last_name="Client",
        role="client",
        password=None,
    )
    login(request, guest, backend="django.contrib.auth.backends.ModelBackend")
    return render(request, "auth/guest_login.html", {"guest": guest})


def register_client(request):
    if request.method == "POST":
        form = PsychologistPersonalForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if not data.get("email") or not data.get("password"):
                messages.error(request, "Email або пароль не можуть бути порожніми.")
                return render(request, "auth/register_client.html", {"form": form})
            user = User.objects.create_user(
                username=data["email"],
                email=data["email"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                patronymic=data["patronymic"],
                birth_date=data["birth_date"],
                phone=data["phone"],
                document_type=data["document_type"],
                document_number=data["document_number"],
                role="client",
                password=data["password"],
            )
            messages.success(request, "Клієнт успішно зареєстрований!")
            return redirect("register_success")
        else:
            messages.error(request, "Будь ласка, перевірте правильність введених даних.")
    else:
        form = PsychologistPersonalForm()
    return render(request, "auth/register_client.html", {"form": form})


def register_psychologist_personal(request):
    if request.method == "POST":
        form = PsychologistPersonalForm(request.POST)
        if form.is_valid():
            cleaned = form.cleaned_data
            if not cleaned.get("email") or not cleaned.get("password"):
                messages.error(request, "Email і пароль є обов’язковими.")
                return render(request, "auth/register_psychologist_personal.html", {"form": form})
            safe_data = cleaned.copy()
            if safe_data.get("birth_date"):
                safe_data["birth_date"] = safe_data["birth_date"].isoformat()
            request.session["psychologist_data"] = safe_data
            return redirect("register_psychologist_professional")
        else:
            messages.error(request, "Будь ласка, валідно заповніть форму.")
    else:
        form = PsychologistPersonalForm()
    return render(request, "auth/register_psychologist_personal.html", {"form": form})


def register_psychologist_professional(request):
    data = request.session.get("psychologist_data")
    if not data:
        return redirect("register_psychologist_personal")
    if data.get("birth_date"):
        data["birth_date"] = date.fromisoformat(data["birth_date"])
    if request.method == "POST":
        form = PsychologistWorkForm(request.POST)
        if form.is_valid():
            user = User(
                username=data["email"],
                email=data["email"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                patronymic=data["patronymic"],
                birth_date=data["birth_date"],
                phone=data["phone"],
                document_type=data["document_type"],
                document_number=data["document_number"],
                role="psychologist",
            )
            user.set_password(data["password"])
            user.save()
            profile = form.save(commit=False)
            profile.user = user
            profile.save()
            if "psychologist_data" in request.session:
                del request.session["psychologist_data"]
            messages.success(request, "Психолог успішно зареєстрований!")
            return redirect("register_success")
        else:
            messages.error(request, "Будь ласка, перевірте введені поля.")
    else:
        form = PsychologistWorkForm()
    return render(request, "auth/register_psychologist_professional.html", {"form": form})


@login_required(login_url="/auth/login/")
def register_success(request):
    return render(request, "auth/register_success.html")
