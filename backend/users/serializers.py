from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework import serializers

from recipes.models import Recipe
from users.models import Follow, User


class CustomUserSerializer(DjoserUserSerializer):
    """
    Базовый сериализатор пользователя, расширяющий Djoser и добавляющий
    поле is_subscribed и абсолютную ссылку на аватар.
    """

    is_subscribed = serializers.SerializerMethodField(read_only=True)
    avatar = serializers.SerializerMethodField(read_only=True)

    class Meta(DjoserUserSerializer.Meta):
        """Meta-класс, определяющий поля и поведение сериализатора."""

        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )
        extra_kwargs = {'password': {'write_only': True}}

    def get_is_subscribed(self, obj):
        """
        Возвращает True, если текущий пользователь подписан на obj.
        """
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author=obj).exists()

    def get_avatar(self, obj):
        """
        Возвращает абсолютный URL аватара, если он существует.
        """
        request = self.context.get('request')
        fileobj = getattr(obj, 'avatar', None)
        if not fileobj or not getattr(fileobj, 'url', None) or not request:
            return None
        try:
            return request.build_absolute_uri(fileobj.url)
        except Exception:
            return fileobj.url

    def create(self, validated_data):
        """
        Создаёт пользователя через менеджер модели.
        """
        return User.objects.create_user(**validated_data)


class CustomUserCreateSerializer(serializers.ModelSerializer):
    """
    Отдельный сериализатор для регистрации пользователя.
    """

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """
        Создаёт нового пользователя через менеджер модели.
        """
        return User.objects.create_user(**validated_data)

    def to_representation(self, instance):
        """
        Возвращает данные без пароля и служебных полей.
        """
        return {
            'id': instance.id,
            'email': instance.email,
            'username': instance.username,
            'first_name': instance.first_name,
            'last_name': instance.last_name,
        }


class ShortRecipeSerializer(serializers.ModelSerializer):
    """
    Короткое представление рецепта для списков подписок и избранного.
    """

    image = serializers.ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(CustomUserSerializer):
    """
    Сериализатор автора, используемый в списке подписок.
    Добавляет список его рецептов и их количество.
    """

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        """
        Возвращает рецепты автора, ограниченные параметром recipes_limit.
        """
        request = self.context.get('request')
        limit = None

        if request:
            try:
                limit = int(request.query_params.get('recipes_limit') or 0)
            except (TypeError, ValueError):
                limit = None

        queryset = obj.recipes.all().order_by('-id')
        if limit:
            queryset = queryset[:limit]

        return ShortRecipeSerializer(
            queryset,
            many=True,
            context={'request': request},
        ).data

    def get_recipes_count(self, obj):
        """
        Возвращает общее количество рецептов автора.
        """
        return obj.recipes.count()


class FollowSerializer(serializers.ModelSerializer):
    """
    Сериализатор создания подписки.
    Проверяет уникальность и запрет самоподписки.
    """

    class Meta:
        model = Follow
        fields = ('user', 'author')
        validators = (
            serializers.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author'),
                message='Подписка уже оформлена',
            ),
        )

    def validate(self, data):
        """
        Запрещает пользователю подписываться на самого себя.
        """
        if data.get('user') == data.get('author'):
            raise serializers.ValidationError({
                'errors': 'Нельзя подписаться на себя'
            })
        return data

    def to_representation(self, instance):
        """
        Возвращает данные подписанного автора в расширенном виде.
        """
        return SubscriptionSerializer(
            instance=instance.author,
            context={'request': self.context.get('request')},
        ).data
