from django.contrib import admin
from .models import User, Department, Role

# admin.site.register(User)
@admin.register(User)
class USerAdmin(admin.ModelAdmin):
    readonly_fields = ["id", 'created_at', 'updated_at']
    list_display = ['username', 'email', 'first_name', 'last_name']

# admin.site.register(Department)
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    readonly_fields = ["id", 'created_at', 'updated_at']
    list_display = ['department_name','description']
admin.site.register(Role)
