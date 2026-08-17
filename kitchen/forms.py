from django import forms
from django.contrib.auth.forms import UserCreationForm

from kitchen.models import Cook, Dish, DishType, Ingredient


class BootstrapFormMixin:
    """Add Bootstrap CSS classes to form fields."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxSelectMultiple):
                css_class = "me-2"
            elif isinstance(widget, forms.CheckboxInput):
                css_class = "form-check-input"
            elif isinstance(widget, forms.Select):
                css_class = "form-select"
            else:
                css_class = "form-control"

            current_classes = widget.attrs.get("class", "")
            widget.attrs["class"] = (
                f"{current_classes} {css_class}".strip()
            )


class CookCreationForm(BootstrapFormMixin, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Cook
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "years_of_experience",
            "password1",
            "password2",
        )


class CookUpdateForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Cook
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "years_of_experience",
        )


class DishForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Dish
        fields = (
            "name",
            "description",
            "price",
            "dish_type",
            "cooks",
            "ingredients",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "cooks": forms.CheckboxSelectMultiple,
            "ingredients": forms.CheckboxSelectMultiple,
        }


class DishTypeForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = DishType
        fields = ("name",)


class IngredientForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ("name",)


class DishSearchForm(BootstrapFormMixin, forms.Form):
    name = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Search by name"}),
    )


class CookSearchForm(BootstrapFormMixin, forms.Form):
    username = forms.CharField(
        max_length=150,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={"placeholder": "Search by username"}
        ),
    )


class DishTypeSearchForm(BootstrapFormMixin, forms.Form):
    name = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Search by name"}),
    )


class IngredientSearchForm(BootstrapFormMixin, forms.Form):
    name = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Search by name"}),
    )
