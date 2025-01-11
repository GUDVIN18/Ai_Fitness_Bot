from django.contrib import admin
from apps.notification.models import *

# Register your models here.
@admin.register(Motivational_Messages)
class Motivational_MessagesAdmin(admin.ModelAdmin):
    fields = [
        "user",
        "text",
        'status',
        "created_at",
    ]
    list_display = (
        "user",
        'status',
        "created_at",
    )
    list_filter = (
        "created_at",
    )
    search_fields = (
        "user",
    )