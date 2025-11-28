from django import forms
from datetime import date
from .models import User, Psychologist
import uuid

DOCUMENT_TYPES = [
    ("passport", "Паспорт"),
    ("idcard", "ID-Карта"),
]

class ClientRegisterForm(forms.ModelForm):
    confirm_data = forms.BooleanField(label='Я підтверджую заяву "Дані достовірні"', required=True)

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "input", "placeholder": "Пароль"}),
        label="Пароль"
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "input", "placeholder": "Повторити пароль"}),
        label="Підтвердження пароля"
    )

    document_type = forms.ChoiceField(
        choices=DOCUMENT_TYPES,
        widget=forms.Select(attrs={"class": "input"}),
        required=True
    )

    class Meta:
        model = User
        fields = [
            "last_name", "first_name", "patronymic", "birth_date",
            "phone", "email", "document_type", "document_number",
            "password", "password2"
        ]
        widgets = {
            "last_name": forms.TextInput(attrs={"placeholder": "Прізвище", "class": "input"}),
            "first_name": forms.TextInput(attrs={"placeholder": "Ім'я", "class": "input"}),
            "patronymic": forms.TextInput(attrs={"placeholder": "По батькові", "class": "input"}),
            "birth_date": forms.TextInput(attrs={
                "placeholder": "Дата народження",
                "onfocus": "(this.type='date')",
                "onblur": "(this.type='text')",
                "class": "input"
            }),
            "phone": forms.TextInput(attrs={"placeholder": "Номер телефону", "id": "phone-field", "class": "input"}),
            "email": forms.EmailInput(attrs={"placeholder": "Електронна пошта", "class": "input"}),
            "document_number": forms.TextInput(attrs={"placeholder": "Номер документа", "class": "input"}),
        }

    def clean_last_name(self):
        v = self.cleaned_data.get("last_name", "")
        if not v.isalpha():
            raise forms.ValidationError("Прізвище має містити лише літери.")
        return v

    def clean_first_name(self):
        v = self.cleaned_data.get("first_name", "")
        if not v.isalpha():
            raise forms.ValidationError("Ім’я має містити лише літери.")
        return v

    def clean_patronymic(self):
        v = self.cleaned_data.get("patronymic", "")
        if v and not v.isalpha():
            raise forms.ValidationError("По батькові має містити лише літери.")
        return v

    def clean_birth_date(self):
        d = self.cleaned_data.get("birth_date")
        if d and d > date.today():
            raise forms.ValidationError("Дата народження не може бути у майбутньому.")
        return d

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()

        if not phone.isdigit():
            raise forms.ValidationError("Після +380 можна вводити лише цифри.")

        if len(phone) != 9:
            raise forms.ValidationError("Номер телефону повинен містити 9 цифр після +380.")

        return phone

    def clean_document_number(self):
        doc = self.cleaned_data.get("document_number", "")
        if not doc.isdigit():
            raise forms.ValidationError("Номер документа має містити лише цифри.")
        if not 5 <= len(doc) <= 15:
            raise forms.ValidationError("Номер документа має бути від 5 до 15 цифр.")
        return doc

    def clean_email(self):
        email = self.cleaned_data.get("email", "")
        if " " in email:
            raise forms.ValidationError("Email не може містити пробіли.")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Користувач з таким email уже існує.")
        return email

    def clean(self):
        cd = super().clean()
        if cd.get("password") != cd.get("password2"):
            raise forms.ValidationError("Паролі не співпадають.")
        return cd

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = uuid.uuid4().hex
        user.set_password(self.cleaned_data["password"])
        user.role = "client"
        if commit:
            user.save()
        return user


class PsychologistPersonalForm(forms.ModelForm):
    confirm_data = forms.BooleanField(label='Я підтверджую заяву "Дані достовірні"', required=True)

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "input", "placeholder": "Пароль"}),
        label="Пароль"
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "input", "placeholder": "Повторити пароль"}),
        label="Підтвердження пароля"
    )

    document_type = forms.ChoiceField(
        choices=DOCUMENT_TYPES,
        widget=forms.Select(attrs={"class": "input"}),
        required=True
    )

    class Meta:
        model = User
        fields = [
            "last_name", "first_name", "patronymic", "birth_date",
            "phone", "email", "document_type", "document_number",
            "password", "password2"
        ]
        widgets = {
            "last_name": forms.TextInput(attrs={"placeholder": "Прізвище", "class": "input"}),
            "first_name": forms.TextInput(attrs={"placeholder": "Ім'я", "class": "input"}),
            "patronymic": forms.TextInput(attrs={"placeholder": "По батькові", "class": "input"}),
            "birth_date": forms.TextInput(attrs={
                "placeholder": "Дата народження",
                "onfocus": "(this.type='date')",
                "onblur": "(this.type='text')",
                "class": "input"
            }),
            "phone": forms.TextInput(attrs={"placeholder": "Номер телефону", "id": "phone-field", "class": "input"}),
            "email": forms.EmailInput(attrs={"placeholder": "Електронна пошта", "class": "input"}),
            "document_number": forms.TextInput(attrs={"placeholder": "Номер документа", "class": "input"}),
        }

    def clean(self):
        cd = super().clean()
        if cd.get("password") != cd.get("password2"):
            raise forms.ValidationError("Паролі не співпадають.")
        return cd

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()

        if not phone.isdigit():
            raise forms.ValidationError("Після +380 можна вводити лише цифри.")

        if len(phone) != 9:
            raise forms.ValidationError("Номер телефону повинен містити 9 цифр після +380.")

        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = uuid.uuid4().hex
        user.set_password(self.cleaned_data["password"])
        user.role = "psychologist"
        if commit:
            user.save()
        return user


class PsychologistWorkForm(forms.ModelForm):
    cancel_policy = forms.ChoiceField(
        label="Політика скасування",
        choices=[
            ("24_hours", "За 24 години"),
            ("12_hours", "За 12 годин"),
            ("6_hours", "За 6 годин"),
        ],
        widget=forms.Select(attrs={"class": "input"}),
        required=True
    )

    consultation_format = forms.ChoiceField(
        label="Формат прийомів",
        choices=[
            ("online", "Онлайн"),
            ("offline", "Офлайн"),
        ],
        widget=forms.Select(attrs={"class": "input"}),
        required=True
    )

    class Meta:
        model = Psychologist
        fields = ["specialization", "language", "about", "cancel_policy", "consultation_format"]
        widgets = {
            "specialization": forms.TextInput(attrs={"placeholder": "Спеціалізація", "class": "input"}),
            "language": forms.TextInput(attrs={"placeholder": "Мова", "class": "input"}),
            "about": forms.Textarea(attrs={"rows": 4, "placeholder": "Про себе", "class": "input"}),
        }

    def clean_about(self):
        v = self.cleaned_data.get("about", "")
        if len(v.strip()) < 10:
            raise forms.ValidationError("Опис про себе повинен містити щонайменше 10 символів.")
        return v
