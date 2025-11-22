import django_filters
from django_filters import filters

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name',
                                     lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(django_filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
        method='filter_tags_or',
    )
    is_favorited = filters.NumberFilter(method='get_favorited')
    is_in_shopping_cart = filters.NumberFilter(method='get_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author',
                  'tags',
                  'is_favorited',
                  'is_in_shopping_cart')

    def get_favorited(self, queryset, name, value):
        user = getattr(self.request, 'user', None)
        if value and user and user.is_authenticated:
            return queryset.filter(favorited_by__user=user)
        return queryset

    def get_in_shopping_cart(self, queryset, name, value):
        user = getattr(self.request, 'user', None)
        if value and user and user.is_authenticated:
            return queryset.filter(in_carts__user=user)
        return queryset

    def filter_tags_or(self, queryset, name, value):
        if value:
            return queryset.filter(tags__in=value).distinct()
        return queryset
