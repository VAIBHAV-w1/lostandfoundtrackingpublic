from django.contrib import admin
from .models import ItemReport, UserProfile, Message

@admin.register(ItemReport)
class ItemReportAdmin(admin.ModelAdmin):
    """Custom administrative interface for overseeing item reports."""
    list_display = ('title', 'report_type', 'category', 'status', 'date_reported', 'user')
    list_filter = ('report_type', 'category', 'status', 'date_reported')
    search_fields = ('title', 'description', 'location_name', 'user__username')
    ordering = ('-date_reported',)
    date_hierarchy = 'date_reported'
    
    fieldsets = (
        ('General Information', {
            'fields': ('title', 'report_type', 'category', 'status', 'user')
        }),
        ('Details', {
            'fields': ('description', 'item_date', 'contact_info', 'photo')
        }),
        ('Location Data', {
            'fields': ('location_name', 'latitude', 'longitude', 'accuracy')
        }),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Administrative view for managing extended user metadata."""
    list_display = ('user', 'address')
    search_fields = ('user__username', 'address')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Internal log of secure user-to-user coordinates."""
    list_display = ('sender', 'recipient', 'item', 'timestamp', 'read')
    list_filter = ('read', 'timestamp')
    search_fields = ('sender__username', 'recipient__username', 'body')
    readonly_fields = ('timestamp',)
