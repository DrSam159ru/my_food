from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from drf_extra_fields.fields import Base64ImageField
from rest_framework import permissions, serializers, status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from core.pagination import CustomPagePagination
from users.models import Follow, User
from users.serializers import (
    CustomUserCreateSerializer,
    CustomUserSerializer,
    FollowSerializer,
    SubscriptionSerializer,
)


class _AvatarInSerializer(serializers.Serializer):
    """Входной сериализатор для загрузки аватара в формате base64."""

    avatar = Base64ImageField(required=True)


class CustomUserViewSet(UserViewSet):
    """
    ViewSet для пользователей, расширяющий Djoser:
    аватар, подписки и список подписок.
    """

    http_method_names = ('get', 'post', 'delete', 'put', 'patch')
    pagination_class = CustomPagePagination
    serializer_class = CustomUserSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'id'
    lookup_value_regex = r'\d+'

    def get_permissions(self):
        """
        Возвращает набор прав в зависимости от действия.
        """
        if self.action in ('retrieve',):
            return [permissions.AllowAny()]
        if self.action in ('list',):
            return [permissions.IsAuthenticatedOrReadOnly()]
        return super().get_permissions()

    @action(
        methods=['put', 'delete'],
        detail=False,
        url_path='me/avatar',
        permission_classes=[permissions.IsAuthenticated],
    )
    def avatar(self, request):
        """
        Обновляет или удаляет аватар текущего пользователя.
        """
        if request.method.lower() == 'put':
            data = _AvatarInSerializer(data=request.data)
            data.is_valid(raise_exception=True)
            request.user.avatar = data.validated_data['avatar']
            request.user.save(update_fields=['avatar'])
            url = request.build_absolute_uri(request.user.avatar.url)
            return Response({'avatar': url}, status=status.HTTP_200_OK)

        if request.user.avatar:
            try:
                request.user.avatar.delete(save=False)
            except Exception:
                pass
            request.user.avatar = None
            request.user.save(update_fields=['avatar'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['get'],
        detail=False,
        url_path='subscriptions',
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscriptions(self, request):
        """
        Возвращает список авторов, на которых подписан текущий пользователь.
        """
        queryset = (
            User.objects.filter(followers__user=request.user)
            .distinct()
            .order_by('id')
        )
        page = self.paginate_queryset(queryset)
        ctx = {'request': request}
        if page is not None:
            data = SubscriptionSerializer(page, many=True, context=ctx).data
            return self.get_paginated_response(data)

        data = SubscriptionSerializer(queryset, many=True, context=ctx).data
        return Response(data, status=status.HTTP_200_OK)

    def _get_user_or_404(self):
        """
        Возвращает пользователя по lookup-полю или выбрасывает 404.
        """
        val = self.kwargs.get(self.lookup_url_kwarg or self.lookup_field)
        if not str(val).isdigit():
            raise NotFound('Пользователь не найден.')
        return get_object_or_404(User, **{self.lookup_field: val})

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscribe(self, request, id=None):
        """
        Создаёт или удаляет подписку текущего пользователя на автора.
        """
        author = self._get_user_or_404()

        if request.method == 'POST':
            if request.user.id == author.id:
                return Response(
                    {'errors': 'Нельзя подписаться на себя'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Follow.objects.filter(
                user=request.user,
                author=author,
            ).exists():
                return Response(
                    {'errors': 'Подписка уже оформлена'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = FollowSerializer(
                data={'user': request.user.id, 'author': author.id},
                context={'request': request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        sub = Follow.objects.filter(user=request.user, author=author).first()
        if not sub:
            return Response(
                {'errors': 'Подписка не найдена'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        sub.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_class(self):
        """
        Возвращает сериализатор в зависимости от действия.
        """
        if self.action == 'create':
            return CustomUserCreateSerializer
        return super().get_serializer_class()
