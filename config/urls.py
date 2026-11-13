from django.contrib import admin
from django.urls import include, path

from apps.common import api_root

admin.site.site_header = "Система регистрации обращений"
admin.site.site_title = "HelpDesk"
admin.site.index_title = "Администрирование"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api_root, name="api-root"),
    path("api/", include("apps.accounts.urls")),
    path("api/", include("apps.catalog.urls")),
    path("api/", include("apps.clients.urls")),
    path("api/", include("apps.tickets.urls")),
    path("api/reports/", include("apps.reports.urls")),
]
