from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from kitchen.models import Cook, Dish, DishType, Ingredient


@admin.register(Cook)
class CookAdmin(UserAdmin):
    list_display = (
        "username",
        "first_name",
        "last_name",
        "years_of_experience",
        "is_staff",
    )
    search_fields = ("username", "first_name", "last_name", "email")
    ordering = ("username",)
    fieldsets = UserAdmin.fieldsets + (
        (
            "Kitchen experience",
            {"fields": ("years_of_experience",)},
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Cook details",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "years_of_experience",
                )
            },
        ),
    )


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ("name", "dish_type", "price")
    list_filter = ("dish_type",)
    search_fields = (
        "name",
        "description",
        "cooks__username",
        "ingredients__name",
    )
    filter_horizontal = ("cooks", "ingredients")


@admin.register(DishType)
class DishTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
