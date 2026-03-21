from django.contrib import admin
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'created_at')
    
    list_filter = ('created_at',)
    
    search_fields = ('first_name', 'last_name', 'email', 'message')
    
    readonly_fields = ('first_name', 'last_name', 'email', 'phone', 'message', 'created_at')
    
    ordering = ('-created_at',)

    def has_add_permission(self, request):
        return False