from django.contrib import admin
from .models import MeetingSummary

@admin.register(MeetingSummary)
class MeetingSummaryAdmin(admin.ModelAdmin):
    list_display = ('title', 'meeting_date', 'created_by', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'summary')
