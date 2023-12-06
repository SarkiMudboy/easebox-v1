from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import UserCreationForm, UserChangeForm
from .models import User, UserAccount, Business, Vehicle, Fleet, IndividualRider, CompanyRider

class BoxUserAdmin(UserAdmin):

    add_form = UserCreationForm
    form = UserChangeForm
    model = User

    list_display = ("email", "phone_number", "is_staff", "is_active")
    list_filter = ("email", "phone_number", "is_staff", "is_active")
    fieldsets = (
        (None, {"fields": ("email", "phone_number", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                ("first_name", "last_name"), "email", "phone_number",
                "password1", "password2", "is_staff",
                "is_active", "groups", "user_permissions",
            )
        }),
    )
    search_fields = ("email",)
    ordering = ("email",)


admin.site.register(User, BoxUserAdmin)

admin.site.register(UserAccount)
admin.site.register(Business)
admin.site.register(Fleet)
admin.site.register(Vehicle)
admin.site.register(IndividualRider)
admin.site.register(CompanyRider)

