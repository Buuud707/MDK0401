
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Requester',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=255, verbose_name='ФИО')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='E-mail')),
                ('phone', models.CharField(blank=True, max_length=32, verbose_name='Телефон')),
                ('position', models.CharField(blank=True, max_length=255, verbose_name='Должность')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создан')),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalog.department', verbose_name='Подразделение')),
            ],
            options={
                'verbose_name': 'Заявитель',
                'verbose_name_plural': 'Заявители',
                'ordering': ['full_name'],
            },
        ),
    ]
