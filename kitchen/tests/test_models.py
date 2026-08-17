from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from kitchen.models import Dish, DishType, Ingredient


class KitchenModelTests(TestCase):
    def setUp(self):
        self.cook = get_user_model().objects.create_user(
            username="chef",
            password="test-password",
            first_name="Alex",
            last_name="Cook",
        )
        self.dish_type = DishType.objects.create(name="Main course")
        self.ingredient = Ingredient.objects.create(name="Tomato")
        self.dish = Dish.objects.create(
            name="Pasta",
            description="Simple tomato pasta",
            price=Decimal("12.50"),
            dish_type=self.dish_type,
        )

    def test_cook_defaults_and_string_representation(self):
        self.assertEqual(self.cook.years_of_experience, 0)
        self.assertEqual(str(self.cook), "chef (Alex Cook)")

    def test_cook_absolute_url(self):
        self.assertEqual(
            self.cook.get_absolute_url(),
            reverse("kitchen:cook-detail", kwargs={"pk": self.cook.pk}),
        )

    def test_simple_model_string_representations(self):
        self.assertEqual(str(self.dish_type), "Main course")
        self.assertEqual(str(self.ingredient), "Tomato")
        self.assertEqual(str(self.dish), "Pasta")

    def test_dish_relations(self):
        self.dish.cooks.add(self.cook)
        self.dish.ingredients.add(self.ingredient)

        self.assertEqual(self.dish.dish_type, self.dish_type)
        self.assertIn(self.dish, self.cook.dishes.all())
        self.assertIn(self.dish, self.ingredient.dishes.all())

    def test_dish_price_must_be_positive(self):
        self.dish.price = Decimal("0.00")

        with self.assertRaises(ValidationError):
            self.dish.full_clean()
