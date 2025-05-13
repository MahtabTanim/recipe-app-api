"""
Django admin Customization
"""

from . import models
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


class CustomUserAdmin(UserAdmin):
    model = models.User
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    ordering = [
        "id",
    ]
    list_display = ["email", "username", "last_name"]
    add_fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "username",
                    "is_admin",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )


admin.site.register(models.User, CustomUserAdmin)
admin.site.register(models.Recipe)
admin.site.register(models.Tag)
admin.site.register(models.Ingredient)
