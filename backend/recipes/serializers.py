from __future__ import annotations

from typing import Any, Dict, List

from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from favorites.models import Favorite
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from shopping.models import ShoppingList
from users.models import Follow, User
from users.serializers import CustomUserSerializer


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов рецептов."""

    class Meta:
        """Метаданные сериализатора тегов."""

        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        """Метаданные сериализатора ингредиентов."""

        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Краткий сериализатор рецепта для списков и вложенных ответов."""

    class Meta:
        """Метаданные краткого сериализатора рецептов."""

        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = fields


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор ингредиентов в рецепте для чтения, с раскрытием полей
    ингредиента.
    """

    id = serializers.IntegerField(source='ingredient.id', read_only=True)
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True,
    )

    class Meta:
        """Метаданные сериализатора ингредиентов рецепта для чтения."""

        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientWriteItemSerializer(serializers.Serializer):
    """Элемент списка ингредиентов при создании или изменении рецепта."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)

    def validate_id(self, value):
        """
        Проверяет существование ингредиента с указанным идентификатором.
        """
        if not Ingredient.objects.filter(id=value).exists():
            raise serializers.ValidationError('Ингредиент не найден.')
        return value


class AuthorMiniSerializer(serializers.ModelSerializer):
    """Укороченный сериализатор автора с признаком подписки и аватаром."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField(read_only=True)

    class Meta:
        """Метаданные краткого сериализатора автора."""

        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )

    def get_avatar(self, obj):
        """
        Возвращает абсолютный URL аватара пользователя, если он доступен.
        """
        request = self.context.get('request')
        fileobj = getattr(obj, 'avatar', None)
        if not fileobj or not getattr(fileobj, 'url', None) or not request:
            return None
        try:
            return request.build_absolute_uri(fileobj.url)
        except Exception:
            return fileobj.url

    def get_is_subscribed(self, obj):
        """
        Возвращает True, если текущий пользователь подписан на автора.
        """
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Follow.objects.filter(user=request.user, author=obj).exists()


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта для чтения с расширенными полями."""

    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        source='recipe_ingredients',
        many=True,
        read_only=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        """Метаданные сериализатора рецепта для чтения."""

        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj: Recipe) -> bool:
        """
        Проверяет, добавлен ли рецепт в избранное текущим пользователем.
        """
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Favorite.objects.filter(
            user=request.user,
            recipe=obj,
        ).exists()

    def get_is_in_shopping_cart(self, obj: Recipe) -> bool:
        """
        Проверяет, находится ли рецепт в списке покупок пользователя.
        """
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return ShoppingList.objects.filter(
            user=request.user,
            recipe=obj,
        ).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта для создания и обновления."""

    ingredients = RecipeIngredientWriteItemSerializer(
        many=True,
        write_only=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    image = Base64ImageField()

    class Meta:
        """Метаданные сериализатора рецепта для записи."""

        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Проводит комплексную валидацию тегов, ингредиентов и времени готовки.
        """
        tags = attrs.get('tags') or []
        if not tags:
            raise serializers.ValidationError({
                'tags': 'Нужно указать хотя бы один тег.'
            })

        tag_ids = [t.id for t in tags]
        if len(tag_ids) != len(set(tag_ids)):
            raise serializers.ValidationError({
                'tags': 'Теги не должны повторяться.'
            })

        items: List[Dict[str, Any]] = attrs.get('ingredients') or []
        if not items:
            raise serializers.ValidationError({
                'ingredients': 'Нужно добавить хотя бы один ингредиент.'
            })

        seen = set()
        for item in items:
            ing_id = item['id']
            if ing_id in seen:
                raise serializers.ValidationError({
                    'ingredients': 'Ингредиенты не должны повторяться.'
                })
            seen.add(ing_id)
            if item['amount'] < 1:
                raise serializers.ValidationError({
                    'ingredients': 'Количество должно быть ≥ 1.'
                })

        if attrs.get('cooking_time', 0) < 1:
            raise serializers.ValidationError({
                'cooking_time': 'Время приготовления должно быть ≥ 1.'
            })

        return attrs

    def to_representation(self, instance: Recipe) -> Dict[str, Any]:
        """
        Представляет рецепт в формате сериализатора для чтения.
        """
        return RecipeReadSerializer(instance, context=self.context).data

    @transaction.atomic
    def create(self, validated_data: Dict[str, Any]) -> Recipe:
        """
        Создаёт рецепт, привязывая теги и ингредиенты в одной транзакции.
        """
        ingredients_data = validated_data.pop('ingredients', [])
        tags = validated_data.pop('tags', [])

        validated_data['author'] = self.context['request'].user

        recipe = super().create(validated_data)

        recipe.tags.set(tags)
        self._set_ingredients(recipe, ingredients_data)
        return recipe

    @transaction.atomic
    def update(
        self,
        instance: Recipe,
        validated_data: Dict[str, Any],
    ) -> Recipe:
        """
        Обновляет рецепт и его связи с тегами и ингредиентами.
        """
        ingredients_data = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)

        instance = super().update(instance, validated_data)

        if tags is not None:
            instance.tags.set(tags)

        if ingredients_data is not None:
            instance.recipe_ingredients.all().delete()
            self._set_ingredients(instance, ingredients_data)

        return instance

    def _set_ingredients(
        self,
        recipe: Recipe,
        items: List[Dict[str, Any]],
    ):
        """
        Создаёт связи RecipeIngredient для указанных ингредиентов.
        """
        bulk = [
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=item['id'],
                amount=item['amount'],
            )
            for item in items
        ]
        RecipeIngredient.objects.bulk_create(bulk)
