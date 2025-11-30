from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='is_expired',
            field=models.BooleanField(default=False),
        ),
    ]
