from django.contrib import admin
from .models import Profile, MaintenanceRequest
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user','role','branch')
@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ('title','branch','hod','status','date_submitted')
    list_filter = ('status','branch')
    search_fields = ('title','description','hod__username')
