import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authorization.models import User, Psychologist

# Создаем тестовых психологов
psychologists_data = [
    {
        'first_name': 'Олег',
        'last_name': 'Сидоренко',
        'email': 'oleg@psychologist.com',
        'experience': 15,
        'price': 2000,
        'rating': 4.9,
        'languages': 'Українська, Англійська'
    },
    {
        'first_name': 'Андрій',
        'last_name': 'Сірко', 
        'email': 'andrii@psychologist.com',
        'experience': 10,
        'price': 2000,
        'rating': 4.5,
        'languages': 'Українська, Англійська'
    },
    {
        'first_name': 'Інна',
        'last_name': 'Міцкевич',
        'email': 'inna@psychologist.com',
        'experience': 5,
        'price': 1900,
        'rating': 4.0,
        'languages': 'Українська, Англійська'
    },
    {
        'first_name': 'Павло',
        'last_name': 'Сидоренко',
        'email': 'pavlo@psychologist.com',
        'experience': 1,
        'price': 1600,
        'rating': 4.7,
        'languages': 'Українська'
    }
]

for psych_data in psychologists_data:
    # Создаем пользователя
    user = User.objects.create_user(
        username=psych_data['email'],
        email=psych_data['email'],
        first_name=psych_data['first_name'],
        last_name=psych_data['last_name'],
        password='testpass123',
        role='psychologist'
    )
    
    # Создаем профиль психолога
    psychologist = Psychologist.objects.create(
        user=user,
        experience=psych_data['experience'],
        price=psych_data['price'],
        rating=psych_data['rating'],
        languages=psych_data['languages']
    )
    
    print(f'Создан психолог: {psych_data["first_name"]} {psych_data["last_name"]}')

print('Все тестовые психологи созданы!')