from django.contrib import admin
from .models import User, Student, Parent
from .forms import UserCreationForm

# ------------------------------
# UserAdmin simple
# ------------------------------
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    form = UserCreationForm

    list_display = [
        "get_full_name",
        "username",
        "email",
        "is_active",
        "is_student",
        "is_lecturer",
        "is_parent",
        "is_staff",
        "is_superuser",
    ]

    search_fields = ["username", "first_name", "last_name", "email"]

    # Actions de suppression Django par défaut
    actions = ["delete_selected"]

# ------------------------------
# Enregistrement des autres modèles
# ------------------------------
admin.site.register(Student)
admin.site.register(Parent)
