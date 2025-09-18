from django.contrib import admin
from .models import Attendance

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'status', 'location', 'timestamp']
    search_fields = ['employee__username', 'status']
    list_filter = ['status', 'date']

admin.site.register(Attendance, AttendanceAdmin)
