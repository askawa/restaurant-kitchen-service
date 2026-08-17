from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from kitchen.models import Dish, DishType, Ingredient


class KitchenViewTests(TestCase):
    def setUp(self):
        self.cook = get_user_model().objects.create_user(
            username="chef",
            password="test-password",
            years_of_experience=3,
        )
        self.other_cook = get_user_model().objects.create_user(
            username="assistant",
            password="test-password",
        )
        self.dish_type = DishType.objects.create(name="Main course")
        self.ingredient = Ingredient.objects.create(name="Tomato")
        self.dish = Dish.objects.create(
            name="Pasta",
            description="Simple pasta",
            price=Decimal("12.50"),
            dish_type=self.dish_type,
        )

    def test_anonymous_user_is_redirected_to_login(self):
        for url in (
            reverse("kitchen:index"),
            reverse("kitchen:dish-list"),
            reverse("kitchen:cook-list"),
            reverse("kitchen:dish-type-list"),
            reverse("kitchen:ingredient-list"),
        ):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse("login"), response.url)

    def test_dashboard_counts_objects_and_session_visits(self):
        self.client.force_login(self.cook)

        first_response = self.client.get(reverse("kitchen:index"))
        second_response = self.client.get(reverse("kitchen:index"))

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(first_response.context["num_cooks"], 2)
        self.assertEqual(first_response.context["num_dishes"], 1)
        self.assertEqual(first_response.context["num_dish_types"], 1)
        self.assertEqual(first_response.context["num_ingredients"], 1)
        self.assertEqual(first_response.context["num_visits"], 1)
        self.assertEqual(second_response.context["num_visits"], 2)

    def test_application_pages_are_rendered_for_cook(self):
        self.client.force_login(self.cook)
        urls = (
            reverse("kitchen:dish-list"),
            reverse("kitchen:dish-detail", args=[self.dish.pk]),
            reverse("kitchen:cook-list"),
            reverse("kitchen:cook-detail", args=[self.cook.pk]),
            reverse("kitchen:dish-type-list"),
            reverse("kitchen:ingredient-list"),
        )

        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_dish_search_is_case_insensitive(self):
        Dish.objects.create(
            name="Apple pie",
            price=Decimal("6.00"),
            dish_type=self.dish_type,
        )
        self.client.force_login(self.cook)

        response = self.client.get(
            reverse("kitchen:dish-list"),
            {"q": "PASTA"},
        )

        self.assertEqual(list(response.context["dish_list"]), [self.dish])

    def test_cook_search_is_case_insensitive(self):
        self.client.force_login(self.cook)

        response = self.client.get(
            reverse("kitchen:cook-list"),
            {"q": "ASSIST"},
        )

        self.assertEqual(
            list(response.context["cook_list"]),
            [self.other_cook],
        )

    def test_dish_list_is_paginated_by_five(self):
        for number in range(5):
            Dish.objects.create(
                name=f"Dish {number}",
                price=Decimal("5.00"),
                dish_type=self.dish_type,
            )
        self.client.force_login(self.cook)

        response = self.client.get(reverse("kitchen:dish-list"))

        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["dish_list"]), 5)

    def test_create_dish_type(self):
        self.client.force_login(self.cook)

        response = self.client.post(
            reverse("kitchen:dish-type-create"),
            {"name": "Dessert"},
        )

        self.assertRedirects(response, reverse("kitchen:dish-type-list"))
        self.assertTrue(DishType.objects.filter(name="Dessert").exists())

    def test_update_ingredient(self):
        self.client.force_login(self.cook)

        response = self.client.post(
            reverse("kitchen:ingredient-update", args=[self.ingredient.pk]),
            {"name": "Cherry tomato"},
        )

        self.assertRedirects(response, reverse("kitchen:ingredient-list"))
        self.ingredient.refresh_from_db()
        self.assertEqual(self.ingredient.name, "Cherry tomato")

    def test_delete_dish(self):
        self.client.force_login(self.cook)

        response = self.client.post(
            reverse("kitchen:dish-delete", args=[self.dish.pk]),
        )

        self.assertRedirects(response, reverse("kitchen:dish-list"))
        self.assertFalse(Dish.objects.filter(pk=self.dish.pk).exists())

    def test_create_cook(self):
        self.client.force_login(self.cook)

        response = self.client.post(
            reverse("kitchen:cook-create"),
            {
                "username": "pastry.cook",
                "first_name": "Pat",
                "last_name": "Cook",
                "email": "pat@example.com",
                "years_of_experience": 1,
                "password1": "Strong-test-password-123",
                "password2": "Strong-test-password-123",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            get_user_model().objects.filter(username="pastry.cook").exists()
        )

    def test_assignment_toggle_accepts_post_only(self):
        self.client.force_login(self.cook)
        url = reverse("kitchen:dish-toggle-assign", args=[self.dish.pk])

        self.assertEqual(self.client.get(url).status_code, 405)

        first_response = self.client.post(url)
        self.assertRedirects(
            first_response,
            reverse("kitchen:dish-detail", args=[self.dish.pk]),
        )
        self.assertTrue(self.dish.cooks.filter(pk=self.cook.pk).exists())

        self.client.post(url)
        self.assertFalse(self.dish.cooks.filter(pk=self.cook.pk).exists())
