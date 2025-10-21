from django.contrib import admin
from .models import Profile, MaintenanceRequest

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'branch')
    list_filter = ('role', 'branch')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')

@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'branch', 'hod', 'status', 'date_submitted')
    list_filter = ('status', 'branch', 'date_submitted')
    search_fields = ('title', 'description', 'hod__username', 'hod__first_name', 'hod__last_name')
    ordering = ('-date_submitted',)
