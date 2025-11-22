from __future__ import annotations

from django.db.models import Prefetch, Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from core.pagination import CustomPagePagination
from favorites.models import Favorite
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from recipes.serializers import (
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    ShortRecipeSerializer,
    TagSerializer,
)
from shopping.models import ShoppingList

from .permissions import IsAuthorOrReadOnly


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Просмотр списка тегов и деталей тега (только чтение)."""

    queryset = Tag.objects.all().order_by('id')
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    http_method_names = ('get', 'head', 'options')
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Просмотр списка ингредиентов и поиск по имени (только чтение)."""

    queryset = Ingredient.objects.all().order_by('id')
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    http_method_names = ('get', 'head', 'options')
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """
    CRUD для рецептов с поддержкой фильтров, избранного и списка покупок.
    """

    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPagePagination

    def get_queryset(self):
        """
        Базовый queryset с оптимизированными выборками.
        Фильтрация выполняется через RecipeFilter.
        """
        return (
            Recipe.objects.select_related('author').prefetch_related(
                'tags',
                Prefetch(
                    'recipe_ingredients',
                    queryset=RecipeIngredient.objects.select_related(
                        'ingredient'
                    ),
                ),
                'favorited_by',
                'in_carts',
            ).order_by('-id')
        )

    def get_permissions(self):
        """
        Возвращает набор прав в зависимости от действия и HTTP-метода.
        """
        if self.request.method in SAFE_METHODS:
            return [IsAuthorOrReadOnly()]
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAuthenticated(), IsAuthorOrReadOnly()]
        return super().get_permissions()

    def get_serializer_class(self):
        """
        Выбирает сериализатор для чтения или записи рецепта.
        """
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        """
        Добавляет рецепт в избранное текущего пользователя.
        """
        recipe = self.get_object()
        obj, created = Favorite.objects.get_or_create(
            user=request.user,
            recipe=recipe,
        )
        if not created:
            return Response(
                {'detail': 'Рецепт уже в избранном.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = ShortRecipeSerializer(recipe).data
        return Response(data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def favorite_delete(self, request, pk=None):
        """
        Удаляет рецепт из избранного текущего пользователя.
        """
        recipe = self.get_object()
        deleted, _ = Favorite.objects.filter(
            user=request.user,
            recipe=recipe,
        ).delete()
        if not deleted:
            return Response(
                {'detail': 'Этого рецепта не было в избранном.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='shopping_cart',
    )
    def shopping_cart(self, request, pk=None):
        """
        Добавляет рецепт в список покупок текущего пользователя.
        """
        recipe = self.get_object()
        obj, created = ShoppingList.objects.get_or_create(
            user=request.user,
            recipe=recipe,
        )
        if not created:
            return Response(
                {'detail': 'Рецепт уже в списке покупок.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = ShortRecipeSerializer(recipe).data
        return Response(data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def shopping_cart_delete(self, request, pk=None):
        """
        Удаляет рецепт из списка покупок текущего пользователя.
        """
        recipe = self.get_object()
        deleted, _ = ShoppingList.objects.filter(
            user=request.user,
            recipe=recipe,
        ).delete()
        if not deleted:
            return Response(
                {'detail': 'Этого рецепта не было в списке покупок.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        """
        Формирует текстовый файл со сводным списком покупок пользователя.
        """
        recipe_ids = ShoppingList.objects.filter(
            user=request.user
        ).values_list('recipe_id', flat=True)

        rows = (
            RecipeIngredient.objects
            .filter(recipe_id__in=recipe_ids)
            .values(
                'ingredient__name',
                'ingredient__measurement_unit',
            )
            .annotate(total_amount=Sum('amount'))
            .order_by('ingredient__name')
        )

        lines = []
        for row in rows:
            name = row['ingredient__name']
            unit = row['ingredient__measurement_unit']
            amount = row['total_amount']
            lines.append(f'{name}: {amount} {unit}')

        content = '\n'.join(lines) if lines else 'Список покупок пуст.'
        response = HttpResponse(
            content,
            content_type='text/plain; charset=utf-8',
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        """
        Возвращает короткую ссылку на рецепт, если она существует.
        """
        recipe = self.get_object()
        code = getattr(
            getattr(recipe, 'shortlink', None),
            'code',
            str(recipe.pk),
        )
        url = request.build_absolute_uri(f'/s/{code}')
        return Response({'short-link': url}, status=status.HTTP_200_OK)
