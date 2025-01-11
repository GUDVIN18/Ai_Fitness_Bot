# Register your models here.
from django.contrib import admin
from .models import *




# admin.site.register(Payment)




@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    fields = [
        "tg_id",
        "subscription",
        "subscribe_data_start",
        "subscribe_data_end",
        "first_name",
        "last_name",
        "username",
        "language",
        "premium",
        "state",
        "language_chooce",
        "gender",
        "age",
        "massa",
        "height",
        "purpose",
        "training_frequency",
        "allergies",
        "protein",
        "products",
        "council",
        "last_message_id",  # Оставлено только одно упоминание
        "last_input_message_id",
        "temporary_training_id",
    ]
    list_display = (
        "tg_id",
        "first_name",
        "subscription",
        "username",
        "state",
    )
    list_filter = (
        "tg_id",
        "subscription",
        "username",
    )
    search_fields = (
        "tg_id",
        "username",
        "id"
    )


class Bot_ButtonStackedInline(admin.StackedInline):
    model = Bot_Button
    extra = 1
    fields = (
        ('text', 'data',),
    )


@admin.register(Bot_Message)
class Bot_MessageAdmin(admin.ModelAdmin):
    inlines = [Bot_ButtonStackedInline]
    fields = [
        "text",
        "current_state",
        "next_state",
        "anyway_link",
        "handler",
    ]
    list_display = (
        "text", 
        "current_state",
        "next_state",
        "handler",
    )
    list_filter = (
        "handler",
    )
    search_fields = (
        "handler",
    )



@admin.register(Bot_Commands)
class Bot_CommandsAdmin(admin.ModelAdmin):
    fields = [
        "text",
        "trigger",
    ]
    list_display = (
        "text",
        "trigger",
    )
    list_filter = (
        "text",
        "trigger",
    )
    search_fields = (
        "text",
        "trigger",
    )






@admin.register(Bot_Button)
class Bot_ButtonAdmin(admin.ModelAdmin):
    fields = [
        "text",
        "message_trigger",
        "data"
    ]
    list_display = (
        "text",
        "message_trigger",
    )
    list_filter = (
        "text",
        "message_trigger",
    )
    search_fields = (
        "text",
        "message_trigger",
    )




@admin.register(UserTraining)
class UserTrainingAdmin(admin.ModelAdmin):
    fields = [
        "user",
        "name_traning",
        "training_data",
        "status",
    ]
    list_display = (
        "id",
        "user",
        "name_traning",
        "status",
        "training_data",
    )


