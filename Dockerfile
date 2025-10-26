FROM python:3.13.2-slim

WORKDIR /app

COPY requirements.txt .
RUN apt-get update && apt-get install -y curl && apt-get clean
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD python manage.py migrate \
    && python manage.py shell -c "from django.contrib.auth import get_user_model; U=get_user_model(); U.objects.filter(username='root').exists() or U.objects.create_superuser('root','root@example.com','root')" \
    && python manage.py collectstatic --no-input \
    && gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120 --log-level info
