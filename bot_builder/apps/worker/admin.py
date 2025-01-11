from django.contrib import admin
from .models import *

# admin.py
from django.contrib import admin
from django.utils.safestring import mark_safe
from django import forms
import json

class EventsAdminForm(forms.ModelForm):
    # Добавляем текстовое поле для редактирования JSON
    formatted_json = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 20, 'cols': 80}),
        required=False,
        label='JSON данные'
    )

    class Meta:
        model = Events
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # При инициализации формы форматируем JSON
        if self.instance.update_data:
            self.fields['formatted_json'].initial = json.dumps(
                self.instance.update_data, 
                indent=4,
                ensure_ascii=False
            )

    def clean_formatted_json(self):
        # Проверяем и преобразуем JSON обратно в словарь
        try:
            json_data = self.cleaned_data['formatted_json']
            if json_data:
                return json.loads(json_data)
            return {}
        except json.JSONDecodeError:
            raise forms.ValidationError("Некорректный формат JSON")

@admin.register(Events)
class EventsAdmin(admin.ModelAdmin):
    form = EventsAdminForm
    
    fields = [
        "user",
        "status",
        'formatted_json',  # Используем новое поле вместо update_data
        'task_id',
    ]
    
    list_display = (
        "user",
        "status",
        'task_id',
    )
    
    list_filter = (
        "user",
        "status",
    )
    
    search_fields = (
        "user",
        "status",
    )

    def save_model(self, request, obj, form, change):
        # Сохраняем отформатированный JSON в поле update_data
        if 'formatted_json' in form.cleaned_data:
            obj.update_data = form.cleaned_data['formatted_json']
        super().save_model(request, obj, form, change)