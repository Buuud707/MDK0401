"""Демо-данные: python manage.py seed_demo"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.catalog.models import Category, Department, Priority
from apps.clients.models import Requester
from apps.tickets.models import Ticket

User = get_user_model()


class Command(BaseCommand):
    help = "Создаёт демонстрационные данные (пользователи, справочники, обращения)"

    def handle(self, *args, **options):
        def mk_user(username, password, role, name, **extra):
            user, created = User.objects.get_or_create(
                username=username, defaults={"role": role, "full_name": name, **extra}
            )
            if created:
                user.set_password(password)
                user.save()
            return user

        mk_user("admin_demo", "Admin12345!", "admin", "Администратор Системы",
                is_staff=True, is_superuser=True)
        op1 = mk_user("operator1", "Operator12345!", "operator", "Петров Пётр")
        op2 = mk_user("operator2", "Operator12345!", "operator", "Сидорова Анна")
        mk_user("manager1", "Manager12345!", "manager", "Орлов Олег")

        depts = {n: Department.objects.get_or_create(name=n)[0]
                 for n in ("Бухгалтерия", "Учебная часть", "Библиотека", "Деканат")}
        cats = {n: Category.objects.get_or_create(name=n)[0]
                for n in ("Оборудование", "Программное обеспечение", "Сеть", "Учётные записи")}
        prios = {}
        for name, level, sla in (("Низкий", 1, 72), ("Средний", 2, 24), ("Высокий", 3, 8), ("Критический", 4, 2)):
            prios[name] = Priority.objects.get_or_create(
                name=name, defaults={"level": level, "sla_hours": sla})[0]

        people = [
            ("Иванов Иван", "ivanov@college.example", "Бухгалтерия"),
            ("Петрова Алла", "petrova@college.example", "Учебная часть"),
            ("Сидоров Дмитрий", "sidorov@college.example", "Библиотека"),
            ("Кузнецова Мария", "kuznetsova@college.example", "Деканат"),
        ]
        reqs = [Requester.objects.get_or_create(
            email=e, defaults={"full_name": n, "department": depts[d]})[0] for n, e, d in people]

        if Ticket.objects.exists():
            self.stdout.write("Обращения уже есть — пропускаю создание.")
            return

        items = [
            ("Не работает проектор в аудитории 205", 0, "Оборудование", "Высокий", "new"),
            ("Нет доступа к учебной системе", 1, "Учётные записи", "Средний", "in_progress"),
            ("Ошибка при печати на принтере", 2, "Оборудование", "Низкий", "resolved"),
            ("Не открывается 1С", 0, "Программное обеспечение", "Критический", "waiting"),
            ("Пропадает Wi-Fi в библиотеке", 2, "Сеть", "Средний", "closed"),
            ("Сброс пароля", 3, "Учётные записи", "Низкий", "resolved"),
            ("Установить Office на новый ПК", 1, "Программное обеспечение", "Средний", "new"),
            ("Медленный интернет в деканате", 3, "Сеть", "Высокий", "in_progress"),
        ]
        for i, (title, r, cat, prio, target) in enumerate(items):
            op = op1 if i % 2 == 0 else op2
            t = Ticket.objects.create(
                title=title, description=f"Описание: {title.lower()}.",
                requester=reqs[r], category=cats[cat], priority=prios[prio], created_by=op1,
            )
            if target == "new":
                continue
            t.assign(op, by=op)
            if target == "waiting":
                t.change_status("waiting", op, "Ждём ответ заявителя")
            elif target in ("resolved", "closed"):
                t.change_status("resolved", op, "Проблема устранена")
                if target == "closed":
                    t.change_status("closed", op, "Подтверждено заявителем")
            if i % 3 == 0:
                t.comments.create(author=op, text="Взял в работу, уточняю детали.")

        self.stdout.write(self.style.SUCCESS(
            "Готово. Вход: admin_demo / Admin12345!, operator1 / Operator12345!, manager1 / Manager12345!"))
