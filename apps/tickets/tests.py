from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.catalog.models import Category, Department, Priority
from apps.clients.models import Requester
from apps.tickets.models import Ticket

User = get_user_model()
PASSWORD = "Str0ngPass!2026"


class BaseAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user("adm", password=PASSWORD, role="admin")
        cls.operator = User.objects.create_user("op", password=PASSWORD, role="operator")
        cls.operator2 = User.objects.create_user("op2", password=PASSWORD, role="operator")
        cls.manager = User.objects.create_user("mgr", password=PASSWORD, role="manager")
        cls.dept = Department.objects.create(name="Бухгалтерия")
        cls.cat = Category.objects.create(name="Оборудование")
        cls.prio = Priority.objects.create(name="Высокий", level=3, sla_hours=4)
        cls.requester = Requester.objects.create(
            full_name="Иванов И.И.", email="ivanov@example.com", department=cls.dept
        )

    def make_ticket(self, **kwargs):
        data = dict(
            title="Не работает принтер", description="Не печатает",
            requester=self.requester, category=self.cat, priority=self.prio,
            created_by=self.operator,
        )
        data.update(kwargs)
        return Ticket.objects.create(**data)

    def payload(self):
        return {
            "title": "Не работает проектор", "description": "Ауд. 205",
            "requester": self.requester.pk, "category": self.cat.pk, "priority": self.prio.pk,
        }


class TicketApiTests(BaseAPITest):
    def test_create_sets_due_date_and_creator(self):
        self.client.force_authenticate(self.operator)
        resp = self.client.post("/api/tickets/", self.payload(), format="json")
        self.assertEqual(resp.status_code, 201, resp.data)
        ticket = Ticket.objects.get(pk=resp.data["id"])
        self.assertEqual(ticket.status, "new")
        self.assertEqual(ticket.created_by, self.operator)
        delta = ticket.due_at - ticket.created_at
        self.assertLess(abs(delta - timedelta(hours=4)), timedelta(seconds=5))

    def test_manager_is_read_only(self):
        self.client.force_authenticate(self.manager)
        self.assertEqual(self.client.get("/api/tickets/").status_code, 200)
        resp = self.client.post("/api/tickets/", self.payload(), format="json")
        self.assertEqual(resp.status_code, 403)

    def test_anonymous_gets_401(self):
        self.assertEqual(self.client.get("/api/tickets/").status_code, 401)

    def test_assign_moves_new_to_in_progress_and_logs(self):
        ticket = self.make_ticket()
        self.client.force_authenticate(self.operator)
        resp = self.client.post(f"/api/tickets/{ticket.pk}/assign/", {}, format="json")
        self.assertEqual(resp.status_code, 200, resp.data)
        ticket.refresh_from_db()
        self.assertEqual(ticket.assignee, self.operator)
        self.assertEqual(ticket.status, "in_progress")
        self.assertEqual(ticket.logs.count(), 1)

    def test_cannot_assign_manager(self):
        ticket = self.make_ticket()
        self.client.force_authenticate(self.admin)
        resp = self.client.post(
            f"/api/tickets/{ticket.pk}/assign/", {"assignee": self.manager.pk}, format="json"
        )
        self.assertEqual(resp.status_code, 400)

    def test_invalid_transition_rejected(self):
        ticket = self.make_ticket()
        self.client.force_authenticate(self.operator)
        resp = self.client.post(f"/api/tickets/{ticket.pk}/status/", {"status": "resolved"}, format="json")
        self.assertEqual(resp.status_code, 400)
        ticket.refresh_from_db()
        self.assertEqual(ticket.status, "new")

    def test_resolve_sets_resolved_at_and_reopen_clears_it(self):
        ticket = self.make_ticket()
        ticket.assign(self.operator, by=self.operator)
        self.client.force_authenticate(self.operator)
        resp = self.client.post(f"/api/tickets/{ticket.pk}/status/", {"status": "resolved"}, format="json")
        self.assertEqual(resp.status_code, 200, resp.data)
        ticket.refresh_from_db()
        self.assertIsNotNone(ticket.resolved_at)
        resp = self.client.post(f"/api/tickets/{ticket.pk}/status/", {"status": "in_progress"}, format="json")
        self.assertEqual(resp.status_code, 200)
        ticket.refresh_from_db()
        self.assertIsNone(ticket.resolved_at)

    def test_comments(self):
        ticket = self.make_ticket()
        self.client.force_authenticate(self.operator)
        resp = self.client.post(f"/api/tickets/{ticket.pk}/comments/", {"text": "Принято"}, format="json")
        self.assertEqual(resp.status_code, 201)
        resp = self.client.get(f"/api/tickets/{ticket.pk}/")
        self.assertEqual(len(resp.data["comments"]), 1)
        self.assertEqual(resp.data["comments"][0]["author"], self.operator.pk)

    def test_filters(self):
        self.make_ticket(title="Первое")
        second = self.make_ticket(title="Второе")
        second.assign(self.operator2, by=self.admin)
        self.client.force_authenticate(self.operator)
        resp = self.client.get("/api/tickets/?status=in_progress")
        self.assertEqual(resp.data["count"], 1)
        self.assertEqual(resp.data["results"][0]["title"], "Второе")
        resp = self.client.get(f"/api/tickets/?assignee={self.operator2.pk}")
        self.assertEqual(resp.data["count"], 1)
        resp = self.client.get("/api/tickets/?search=Первое")
        self.assertEqual(resp.data["count"], 1)

    def test_overdue(self):
        self.make_ticket(title="Просрочено", due_at=timezone.now() - timedelta(hours=1))
        self.make_ticket(title="В срок")
        self.client.force_authenticate(self.operator)
        resp = self.client.get("/api/tickets/?overdue=1")
        self.assertEqual(resp.data["count"], 1)
        self.assertTrue(resp.data["results"][0]["is_overdue"])

    def test_only_admin_deletes(self):
        ticket = self.make_ticket()
        self.client.force_authenticate(self.operator)
        self.assertEqual(self.client.delete(f"/api/tickets/{ticket.pk}/").status_code, 403)
        self.client.force_authenticate(self.admin)
        self.assertEqual(self.client.delete(f"/api/tickets/{ticket.pk}/").status_code, 204)

    def test_requester_with_tickets_cannot_be_deleted(self):
        self.make_ticket()
        self.client.force_authenticate(self.operator)
        resp = self.client.delete(f"/api/requesters/{self.requester.pk}/")
        self.assertEqual(resp.status_code, 409)

    def test_catalog_write_admin_only(self):
        self.client.force_authenticate(self.operator)
        self.assertEqual(self.client.get("/api/categories/").status_code, 200)
        resp = self.client.post("/api/categories/", {"name": "Сеть"}, format="json")
        self.assertEqual(resp.status_code, 403)
        self.client.force_authenticate(self.admin)
        resp = self.client.post("/api/categories/", {"name": "Сеть"}, format="json")
        self.assertEqual(resp.status_code, 201)
