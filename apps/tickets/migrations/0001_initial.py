
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('catalog', '0001_initial'),
        ('clients', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Тема')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('status', models.CharField(choices=[('new', 'Новое'), ('in_progress', 'В работе'), ('waiting', 'Ожидает ответа'), ('resolved', 'Решено'), ('closed', 'Закрыто')], default='new', max_length=20, verbose_name='Статус')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлено')),
                ('due_at', models.DateTimeField(blank=True, null=True, verbose_name='Срок решения')),
                ('resolved_at', models.DateTimeField(blank=True, null=True, verbose_name='Решено')),
                ('assignee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_tickets', to=settings.AUTH_USER_MODEL, verbose_name='Исполнитель')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='catalog.category', verbose_name='Категория')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_tickets', to=settings.AUTH_USER_MODEL, verbose_name='Зарегистрировал')),
                ('priority', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='catalog.priority', verbose_name='Приоритет')),
                ('requester', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='tickets', to='clients.requester', verbose_name='Заявитель')),
            ],
            options={
                'verbose_name': 'Обращение',
                'verbose_name_plural': 'Обращения',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='StatusLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('old_status', models.CharField(choices=[('new', 'Новое'), ('in_progress', 'В работе'), ('waiting', 'Ожидает ответа'), ('resolved', 'Решено'), ('closed', 'Закрыто')], max_length=20, verbose_name='Был')),
                ('new_status', models.CharField(choices=[('new', 'Новое'), ('in_progress', 'В работе'), ('waiting', 'Ожидает ответа'), ('resolved', 'Решено'), ('closed', 'Закрыто')], max_length=20, verbose_name='Стал')),
                ('changed_at', models.DateTimeField(auto_now_add=True, verbose_name='Когда')),
                ('note', models.CharField(blank=True, max_length=255, verbose_name='Примечание')),
                ('changed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Кто изменил')),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='tickets.ticket')),
            ],
            options={
                'verbose_name': 'Запись журнала',
                'verbose_name_plural': 'Журнал статусов',
                'ordering': ['changed_at', 'id'],
            },
        ),
        migrations.CreateModel(
            name='TicketComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Текст')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создан')),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='tickets.ticket')),
            ],
            options={
                'verbose_name': 'Комментарий',
                'verbose_name_plural': 'Комментарии',
                'ordering': ['created_at'],
            },
        ),
    ]
