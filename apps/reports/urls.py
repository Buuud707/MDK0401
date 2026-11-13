from django.urls import path

from .views import ExportCsvView, KpiView

urlpatterns = [
    path("kpi/", KpiView.as_view(), name="reports-kpi"),
    path("export/", ExportCsvView.as_view(), name="reports-export"),
]
