from recipes.models import Recipe
from recipes.serializers import ShortRecipeSerializer


class FavoriteSerializer(ShortRecipeSerializer):
    """Сериализатор рецептов, добавленных пользователем в избранное."""

    class Meta(ShortRecipeSerializer.Meta):
        """Метаданные сериализатора избранных рецептов."""

        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = fields
