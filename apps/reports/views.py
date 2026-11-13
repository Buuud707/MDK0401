import csv

from django.db.models import Count, F
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tickets.models import Ticket


class KpiView(APIView):
    """GET /api/reports/kpi/ — показатели службы поддержки."""

    def get(self, request):
        qs = Ticket.objects.all()
        now = timezone.now()

        by_status = {code: 0 for code, _ in Ticket.Status.choices}
        for row in qs.values("status").annotate(c=Count("id")):
            by_status[row["status"]] = row["c"]

        open_qs = qs.exclude(status__in=Ticket.FINAL_STATUSES)
        done = qs.filter(resolved_at__isnull=False)
        pairs = list(done.values_list("created_at", "resolved_at"))
        avg_hours = None
        if pairs:
            total = sum((r - c).total_seconds() for c, r in pairs)
            avg_hours = round(total / len(pairs) / 3600, 2)
        in_sla = done.filter(resolved_at__lte=F("due_at")).count()

        return Response({
            "total": qs.count(),
            "open": open_qs.count(),
            "overdue": open_qs.filter(due_at__lt=now).count(),
            "resolved": done.count(),
            "by_status": by_status,
            "avg_resolution_hours": avg_hours,
            "sla_compliance_percent": round(in_sla / len(pairs) * 100, 1) if pairs else None,
            "by_category": [
                {"category": r["category__name"], "count": r["c"]}
                for r in qs.values("category__name").annotate(c=Count("id")).order_by("-c")
            ],
            "by_priority": [
                {"priority": r["priority__name"], "count": r["c"]}
                for r in qs.values("priority__name", "priority__level")
                .annotate(c=Count("id")).order_by("-priority__level")
            ],
            "by_assignee": [
                {"assignee": r["assignee__username"], "count": r["c"]}
                for r in qs.exclude(assignee__isnull=True)
                .values("assignee__username").annotate(c=Count("id")).order_by("-c")
            ],
        })


class ExportCsvView(APIView):
    """GET /api/reports/export/ — выгрузка обращений в CSV."""

    def get(self, request):
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="obrashcheniya.csv"'
        response.write("\ufeff")
        writer = csv.writer(response, delimiter=";")
        writer.writerow(["Номер", "Тема", "Заявитель", "Категория", "Приоритет",
                         "Статус", "Исполнитель", "Создано", "Срок", "Решено"])
        qs = Ticket.objects.select_related("requester", "category", "priority", "assignee")
        for t in qs:
            writer.writerow([
                t.number, t.title, t.requester.full_name, t.category.name, t.priority.name,
                t.get_status_display(), str(t.assignee) if t.assignee else "",
                timezone.localtime(t.created_at).strftime("%d.%m.%Y %H:%M"),
                timezone.localtime(t.due_at).strftime("%d.%m.%Y %H:%M") if t.due_at else "",
                timezone.localtime(t.resolved_at).strftime("%d.%m.%Y %H:%M") if t.resolved_at else "",
            ])
        return response
