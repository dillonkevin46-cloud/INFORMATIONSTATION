from django.contrib import admin
from .models import Ticket, TicketMessage, TimeEntry

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'client', 'assigned_to', 'created_at')
    list_filter = ('status', 'priority', 'client')
    search_fields = ('title', 'description')

@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'author', 'content_snippet', 'created_at', 'is_internal')
    list_filter = ('is_internal',)

    def content_snippet(self, obj):
        return obj.content[:50]

@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'staff', 'start_time', 'duration_minutes')
    list_filter = ('staff', 'ticket')
