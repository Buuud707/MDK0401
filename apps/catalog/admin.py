from django.contrib import admin

from .models import Category, Department, Priority


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Priority)
class PriorityAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "level", "sla_hours")
    search_fields = ("name",)
