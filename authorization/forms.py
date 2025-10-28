from django import forms
from datetime import date
from .models import User, Psychologist


class PsychologistPersonalForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="Пароль"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="Підтвердження пароля"
    )

    class Meta:
        model = User
        fields = [
            "last_name",
            "first_name",
            "patronymic",
            "birth_date",
            "phone",
            "email",
            "document_type",
            "document_number",
            "password",
            "password2",
        ]
        labels = {
            "last_name": "Прізвище",
            "first_name": "Ім’я",
            "patronymic": "По батькові",
            "birth_date": "Дата народження",
            "phone": "Номер телефону",
            "email": "Електронна пошта",
            "document_type": "Тип документа",
            "document_number": "Номер документа",
        }
        widgets = {
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "patronymic": forms.TextInput(attrs={"class": "form-control"}),
            "birth_date": forms.DateInput(attrs={
                "type": "date",
                "class": "form-control"
            }),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "+380..."}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "document_type": forms.Select(
                choices=[
                    ("passport", "Паспорт"),
                    ("id_card", "ID-карта"),
                ],
                attrs={"class": "form-control"}
            ),
            "document_number": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean_last_name(self):
        value = self.cleaned_data.get("last_name", "")
        if not value.isalpha():
            raise forms.ValidationError("Прізвище має містити лише літери.")
        if " " in value:
            raise forms.ValidationError("Прізвище не може містити пробіли.")
        return value.strip()

    def clean_first_name(self):
        value = self.cleaned_data.get("first_name", "")
        if not value.isalpha():
            raise forms.ValidationError("Ім’я має містити лише літери.")
        if " " in value:
            raise forms.ValidationError("Ім’я не може містити пробіли.")
        return value.strip()

    def clean_patronymic(self):
        value = self.cleaned_data.get("patronymic", "")
        if value and not value.isalpha():
            raise forms.ValidationError("По батькові має містити лише літери.")
        return value.strip()

    def clean_birth_date(self):
        bdate = self.cleaned_data.get("birth_date")
        if bdate and bdate > date.today():
            raise forms.ValidationError("Дата народження не може бути у майбутньому.")
        return bdate

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "")
        if " " in phone:
            raise forms.ValidationError("Номер телефону не може містити пробіли.")
        if not phone.startswith("+380") and not phone.startswith("0"):
            raise forms.ValidationError("Номер телефону повинен починатися з +380 або 0.")
        if len(phone) < 10 or len(phone) > 13:
            raise forms.ValidationError("Некоректна довжина номера телефону.")
        if not phone.replace("+", "").isdigit():
            raise forms.ValidationError("Номер телефону має містити лише цифри.")
        return phone

    def clean_document_number(self):
        doc = self.cleaned_data.get("document_number", "")
        if not doc.isdigit():
            raise forms.ValidationError("Номер документа має містити лише цифри.")
        if len(doc) < 5 or len(doc) > 15:
            raise forms.ValidationError("Номер документа має бути від 5 до 15 цифр.")
        return doc

    def clean_email(self):
        email = self.cleaned_data.get("email", "")
        if " " in email:
            raise forms.ValidationError("Email не може містити пробіли.")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Користувач з таким email уже існує.")
        return email.strip()

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")
        if password != password2:
            raise forms.ValidationError("Паролі не співпадають.")
        return cleaned_data


class PsychologistWorkForm(forms.ModelForm):
    class Meta:
        model = Psychologist
        fields = ["specialization", "language", "tz", "policy", "about", "format"]
        labels = {
            "specialization": "Спеціалізація",
            "language": "Мова спілкування",
            "tz": "Часовий пояс",
            "policy": "Політика скасування",
            "about": "Про себе",
            "format": "Формат проведення консультацій",
        }
        widgets = {
            "specialization": forms.TextInput(attrs={"class": "form-control"}),
            "language": forms.TextInput(attrs={"class": "form-control"}),
            "tz": forms.TextInput(attrs={"class": "form-control"}),
            "policy": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "about": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "format": forms.Select(
                choices=[
                    ("online", "Онлайн"),
                    ("offline", "Офлайн"),
                ],
                attrs={"class": "form-control"}
            ),
        }

    def clean_specialization(self):
        value = self.cleaned_data.get("specialization", "")
        if len(value) < 3:
            raise forms.ValidationError("Вкажіть коректну спеціалізацію.")
        if any(ch.isdigit() for ch in value):
            raise forms.ValidationError("Спеціалізація не повинна містити цифри.")
        return value.strip()

    def clean_language(self):
        value = self.cleaned_data.get("language", "")
        if len(value) < 2:
            raise forms.ValidationError("Мова повинна містити принаймні 2 символи.")
        if any(ch.isdigit() for ch in value):
            raise forms.ValidationError("Мова не повинна містити цифри.")
        return value.strip()

    def clean_about(self):
        text = self.cleaned_data.get("about", "")
        if len(text.strip()) < 10:
            raise forms.ValidationError("Опис про себе повинен містити щонайменше 10 символів.")
        return text
