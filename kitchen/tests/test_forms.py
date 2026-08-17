from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from kitchen.forms import CookCreationForm, DishForm
from kitchen.models import Dish, DishType, Ingredient


class KitchenFormTests(TestCase):
    def test_cook_creation_form_saves_experience(self):
        form = CookCreationForm(
            data={
                "username": "new.cook",
                "first_name": "New",
                "last_name": "Cook",
                "email": "cook@example.com",
                "years_of_experience": 2,
                "password1": "Strong-test-password-123",
                "password2": "Strong-test-password-123",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        cook = form.save()
        self.assertEqual(cook.years_of_experience, 2)

    def test_dish_form_saves_multiple_relations(self):
        cook_one = get_user_model().objects.create_user(username="cook.one")
        cook_two = get_user_model().objects.create_user(username="cook.two")
        dish_type = DishType.objects.create(name="Soup")
        onion = Ingredient.objects.create(name="Onion")
        potato = Ingredient.objects.create(name="Potato")
        form = DishForm(
            data={
                "name": "Vegetable soup",
                "description": "A basic soup",
                "price": Decimal("7.50"),
                "dish_type": dish_type.pk,
                "cooks": [cook_one.pk, cook_two.pk],
                "ingredients": [onion.pk, potato.pk],
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        dish = form.save()
        self.assertEqual(dish.cooks.count(), 2)
        self.assertEqual(dish.ingredients.count(), 2)
        self.assertTrue(Dish.objects.filter(name="Vegetable soup").exists())
