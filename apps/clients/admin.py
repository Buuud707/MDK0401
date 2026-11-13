from django.contrib import admin

from .models import Requester


@admin.register(Requester)
class RequesterAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "email", "phone", "department")
    list_filter = ("department",)
    search_fields = ("full_name", "email", "phone")
    autocomplete_fields = ("department",)
