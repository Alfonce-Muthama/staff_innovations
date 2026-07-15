from django.contrib import admin
from django.contrib.auth.hashers import make_password
from .models import User, Department, Role


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    readonly_fields = ["id", "created_at", "updated_at"]
    list_display = ["username", "email", "first_name", "last_name"]

    def save_model(self, request, obj, form, change):
        # Hash the password only when it is new or has been changed
        if "password" in form.changed_data:
            obj.password = make_password(obj.password)

        super().save_model(request, obj, form, change)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    readonly_fields = ["id", "created_at", "updated_at"]
    list_display = ["department_name", "description"]


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    readonly_fields = ["id", "created_at", "updated_at"]
    list_display = ["name", "description"]