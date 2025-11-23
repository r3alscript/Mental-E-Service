from django import forms
from datetime import date
from .models import User, Psychologist


class PsychologistPersonalForm(forms.ModelForm):
    confirm_data = forms.BooleanField(
        label='Я підтверджую заяву "Дані достовірні"',
        required=True
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Пароль"
        }),
        label="Пароль"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control", 
            "placeholder": "Повторити пароль"  # ИСПРАВЛЕН плейсхолдер
        }),
        label="Підтвердження пароля"
    )
    tz = forms.ChoiceField(
        choices=[
            ('', 'Оберіть часовий пояс'),
            ('Europe/Kyiv', 'Київ (UTC+2)'),
            ('Europe/London', 'Лондон (UTC+0)'),
            ('Europe/Berlin', 'Берлін (UTC+1)'),
        ],
        label="Часовий пояс",
        widget=forms.Select(attrs={"class": "form-control"})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # УБИРАЕМ значения по умолчанию
        self.fields['document_number'].initial = ''  # Убирает "000000"
        self.fields['email'].initial = ''  # Убирает предзаполнение email
        self.fields['password'].initial = ''  # Убирает предзаполнение пароля
        self.fields['password2'].initial = ''  # Убирает предзаполнение подтверждения пароля
        
        # Обновляем атрибуты для всех полей
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'input'})

    class Meta:
        model = User
        fields = [
            "last_name", "first_name", "patronymic", "birth_date", 
            "phone", "email", "document_type", "document_number",
            "tz", "password", "password2", 
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
            "last_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Прізвище"
            }),
            "first_name": forms.TextInput(attrs={
                "class": "form-control", 
                "placeholder": "Ім'я"
            }),
            "patronymic": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "По батькові" 
            }),
            "birth_date": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Дата народження",
                "onfocus": "(this.type='date')",
                "onblur": "(this.type='text')"
            }),
            "phone": forms.TextInput(attrs={
                "class": "form-control", 
                "placeholder": "+380 Номер телефону"
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Електронна пошта"
            }),
            "document_type": forms.Select(
                choices=[
                    ("", "Оберіть тип документа"),
                    ("passport", "Паспорт"),
                    ("id_card", "ID-карта"),
                ],
                attrs={"class": "form-control"}
            ),
            "document_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Номер документа"
            }),
            # password и password2 УБРАНЫ отсюда - они уже определены выше
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
        # ДОБАВЛЯЕМ проверку подтверждения данных (исправляем комментарий)
        if not cleaned_data.get("confirm_data"):
            raise forms.ValidationError("Підтвердьте, що дані достовірні.")
        return cleaned_data

    # ДОБАВЛЯЕМ метод save для правильного сохранения пароля
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # Хэшируем пароль
        user.role = 'psychologist'  # Устанавливаем роль
        if commit:
            user.save()
        return user

class PsychologistWorkForm(forms.ModelForm):
    class Meta:
        model = Psychologist
        fields = ["specialization", "languages", "about"]
        labels = {
            "specialization": "Спеціалізація",
            "languages": "Мови",
            "about": "Про себе",
        }
        widgets = {
            "specialization": forms.TextInput(attrs={"class": "form-control"}),
            "languages": forms.TextInput(attrs={"class": "form-control"}),
            "about": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def clean_specialization(self):
        value = self.cleaned_data.get("specialization", "")
        if len(value) < 3:
            raise forms.ValidationError("Вкажіть коректну спеціалізацію.")
        if any(ch.isdigit() for ch in value):
            raise forms.ValidationError("Спеціалізація не повинна містити цифри.")
        return value.strip()

    def clean_languages(self):
        value = self.cleaned_data.get("languages", "")
        if len(value) < 2:
            raise forms.ValidationError("Мова повинна містити принаймні 2 символи.")
        return value.strip()

    def clean_about(self):
        text = self.cleaned_data.get("about", "")
        if len(text.strip()) < 10:
            raise forms.ValidationError("Опис про себе повинен містити щонайменше 10 символів.")
        return text
