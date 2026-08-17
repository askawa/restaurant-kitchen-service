"""Views for the restaurant kitchen service."""

from functools import reduce
from operator import or_

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Prefetch, Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from kitchen.forms import (
    CookCreationForm,
    CookUpdateForm,
    DishForm,
    DishTypeForm,
    IngredientForm,
)
from kitchen.models import Cook, Dish, DishType, Ingredient


@login_required
def index(request: HttpRequest) -> HttpResponse:
    """Display a small dashboard with database and visit statistics."""
    num_visits = request.session.get("num_visits", 0) + 1
    request.session["num_visits"] = num_visits

    context = {
        "num_dishes": Dish.objects.count(),
        "num_cooks": Cook.objects.count(),
        "num_dish_types": DishType.objects.count(),
        "num_ingredients": Ingredient.objects.count(),
        "num_visits": num_visits,
    }
    return render(request, "kitchen/index.html", context)


class SearchableListMixin:
    """Add a simple multi-field ``q`` search to a list view."""

    paginate_by = 5
    search_fields: tuple[str, ...] = ()

    def get_query(self) -> str:
        return self.request.GET.get("q", "").strip()

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.get_query()

        if query and self.search_fields:
            conditions = (Q(**{field: query}) for field in self.search_fields)
            queryset = queryset.filter(reduce(or_, conditions)).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.get_query()
        return context


class PageContextMixin:
    """Supply headings and cancel links to the shared form templates."""

    page_title = ""
    cancel_url_name = "kitchen:index"
    cancel_uses_pk = False

    def get_cancel_url(self) -> str:
        if self.cancel_uses_pk:
            return reverse(
                self.cancel_url_name,
                kwargs={"pk": self.kwargs["pk"]},
            )
        return reverse(self.cancel_url_name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            page_title=self.page_title,
            cancel_url=self.get_cancel_url(),
        )
        return context


class FormPageMixin(PageContextMixin):
    template_name = "kitchen/object_form.html"


class DeletePageMixin(PageContextMixin):
    template_name = "kitchen/object_confirm_delete.html"


class DishListView(LoginRequiredMixin, SearchableListMixin, ListView):
    model = Dish
    context_object_name = "dish_list"
    template_name = "kitchen/dish_list.html"
    search_fields = (
        "name__icontains",
        "description__icontains",
        "dish_type__name__icontains",
        "ingredients__name__icontains",
        "cooks__username__icontains",
    )

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("dish_type")
            .prefetch_related("cooks", "ingredients")
            .order_by("name")
        )


class DishDetailView(LoginRequiredMixin, DetailView):
    model = Dish
    context_object_name = "dish"
    template_name = "kitchen/dish_detail.html"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("dish_type")
            .prefetch_related("cooks", "ingredients")
        )


class DishCreateView(LoginRequiredMixin, FormPageMixin, CreateView):
    model = Dish
    form_class = DishForm
    page_title = "Create dish"
    cancel_url_name = "kitchen:dish-list"

    def get_success_url(self) -> str:
        return reverse("kitchen:dish-detail", kwargs={"pk": self.object.pk})


class DishUpdateView(LoginRequiredMixin, FormPageMixin, UpdateView):
    model = Dish
    form_class = DishForm
    page_title = "Update dish"
    cancel_url_name = "kitchen:dish-detail"
    cancel_uses_pk = True

    def get_success_url(self) -> str:
        return reverse("kitchen:dish-detail", kwargs={"pk": self.object.pk})


class DishDeleteView(LoginRequiredMixin, DeletePageMixin, DeleteView):
    model = Dish
    page_title = "Delete dish"
    cancel_url_name = "kitchen:dish-detail"
    cancel_uses_pk = True
    success_url = reverse_lazy("kitchen:dish-list")


@login_required
@require_POST
def toggle_assign_to_dish(request: HttpRequest, pk: int) -> HttpResponse:
    """Assign or unassign the signed-in cook from a dish."""
    dish = get_object_or_404(Dish, pk=pk)

    if dish.cooks.filter(pk=request.user.pk).exists():
        dish.cooks.remove(request.user)
    else:
        dish.cooks.add(request.user)

    return redirect("kitchen:dish-detail", pk=pk)


class CookListView(LoginRequiredMixin, SearchableListMixin, ListView):
    model = Cook
    context_object_name = "cook_list"
    template_name = "kitchen/cook_list.html"
    search_fields = (
        "username__icontains",
        "first_name__icontains",
        "last_name__icontains",
    )

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(dish_count=Count("dishes", distinct=True))
            .order_by("username")
        )


class CookDetailView(LoginRequiredMixin, DetailView):
    model = Cook
    context_object_name = "cook"
    template_name = "kitchen/cook_detail.html"

    def get_queryset(self):
        dishes = Dish.objects.select_related("dish_type").prefetch_related(
            "ingredients"
        )
        return super().get_queryset().prefetch_related(
            Prefetch("dishes", queryset=dishes)
        )


class CookCreateView(LoginRequiredMixin, FormPageMixin, CreateView):
    model = Cook
    form_class = CookCreationForm
    page_title = "Create cook"
    cancel_url_name = "kitchen:cook-list"

    def get_success_url(self) -> str:
        return reverse("kitchen:cook-detail", kwargs={"pk": self.object.pk})


class CookUpdateView(LoginRequiredMixin, FormPageMixin, UpdateView):
    model = Cook
    form_class = CookUpdateForm
    page_title = "Update cook"
    cancel_url_name = "kitchen:cook-detail"
    cancel_uses_pk = True

    def get_success_url(self) -> str:
        return reverse("kitchen:cook-detail", kwargs={"pk": self.object.pk})


class CookDeleteView(LoginRequiredMixin, DeletePageMixin, DeleteView):
    model = Cook
    page_title = "Delete cook"
    cancel_url_name = "kitchen:cook-detail"
    cancel_uses_pk = True
    success_url = reverse_lazy("kitchen:cook-list")


class DishTypeListView(LoginRequiredMixin, SearchableListMixin, ListView):
    model = DishType
    context_object_name = "dish_type_list"
    template_name = "kitchen/dish_type_list.html"
    search_fields = ("name__icontains",)

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(dish_count=Count("dishes", distinct=True))
            .order_by("name")
        )


class DishTypeCreateView(LoginRequiredMixin, FormPageMixin, CreateView):
    model = DishType
    form_class = DishTypeForm
    page_title = "Create dish type"
    cancel_url_name = "kitchen:dish-type-list"
    success_url = reverse_lazy("kitchen:dish-type-list")


class DishTypeUpdateView(LoginRequiredMixin, FormPageMixin, UpdateView):
    model = DishType
    form_class = DishTypeForm
    page_title = "Update dish type"
    cancel_url_name = "kitchen:dish-type-list"
    success_url = reverse_lazy("kitchen:dish-type-list")


class DishTypeDeleteView(LoginRequiredMixin, DeletePageMixin, DeleteView):
    model = DishType
    page_title = "Delete dish type"
    cancel_url_name = "kitchen:dish-type-list"
    success_url = reverse_lazy("kitchen:dish-type-list")


class IngredientListView(LoginRequiredMixin, SearchableListMixin, ListView):
    model = Ingredient
    context_object_name = "ingredient_list"
    template_name = "kitchen/ingredient_list.html"
    search_fields = ("name__icontains",)

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(dish_count=Count("dishes", distinct=True))
            .order_by("name")
        )


class IngredientCreateView(LoginRequiredMixin, FormPageMixin, CreateView):
    model = Ingredient
    form_class = IngredientForm
    page_title = "Create ingredient"
    cancel_url_name = "kitchen:ingredient-list"
    success_url = reverse_lazy("kitchen:ingredient-list")


class IngredientUpdateView(LoginRequiredMixin, FormPageMixin, UpdateView):
    model = Ingredient
    form_class = IngredientForm
    page_title = "Update ingredient"
    cancel_url_name = "kitchen:ingredient-list"
    success_url = reverse_lazy("kitchen:ingredient-list")


class IngredientDeleteView(LoginRequiredMixin, DeletePageMixin, DeleteView):
    model = Ingredient
    page_title = "Delete ingredient"
    cancel_url_name = "kitchen:ingredient-list"
    success_url = reverse_lazy("kitchen:ingredient-list")
