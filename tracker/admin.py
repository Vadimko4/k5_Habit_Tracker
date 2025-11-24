from django.contrib import admin
from .models import Habit


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'execution_time', 'is_pleasant', 'related_habit', 'reward']
    list_filter = ['is_pleasant', 'owner', 'execution_time']
    search_fields = ['name', 'action']
    list_editable = ['is_pleasant']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('related_habit', 'owner')
