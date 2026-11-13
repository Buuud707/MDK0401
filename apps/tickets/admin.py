from django.contrib import admin

from .models import StatusLog, Ticket, TicketComment


class TicketCommentInline(admin.TabularInline):
    model = TicketComment
    extra = 0
    fields = ("text", "author", "created_at")
    readonly_fields = ("author", "created_at")


class StatusLogInline(admin.TabularInline):
    model = StatusLog
    extra = 0
    can_delete = False
    fields = ("old_status", "new_status", "changed_by", "changed_at", "note")
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("number", "title", "requester", "category", "priority",
                    "status", "assignee", "due_at", "overdue")
    list_filter = ("status", "priority", "category", "assignee")
    search_fields = ("title", "description", "requester__full_name")
    autocomplete_fields = ("requester", "category", "priority", "assignee")
    readonly_fields = ("created_by", "created_at", "updated_at", "resolved_at")
    date_hierarchy = "created_at"
    inlines = [TicketCommentInline, StatusLogInline]

    @admin.display(description="Просрочено", boolean=True)
    def overdue(self, obj):
        return obj.is_overdue

    def save_model(self, request, obj, form, change):
        old_status = None
        if not change:
            obj.created_by = request.user
        elif "status" in form.changed_data:
            old_status = form.initial.get("status")
        super().save_model(request, obj, form, change)
        if old_status:
            StatusLog.objects.create(
                ticket=obj, old_status=old_status, new_status=obj.status,
                changed_by=request.user, note="Изменено в админке",
            )

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in instances:
            if isinstance(obj, TicketComment) and not obj.author_id:
                obj.author = request.user
            obj.save()
        for obj in formset.deleted_objects:
            obj.delete()
        formset.save_m2m()
