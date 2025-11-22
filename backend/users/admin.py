from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import Follow, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Конфигурация отображения модели User в админ-панели."""

    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'is_active',
        'is_staff',
    )
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('id',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (
            _('Персональные данные'),
            {'fields': ('first_name', 'last_name', 'email', 'avatar')},
        ),
        (
            _('Права доступа'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            },
        ),
        (_('Даты'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'username',
                    'email',
                    'first_name',
                    'last_name',
                    'password1',
                    'password2',
                ),
            },
        ),
    )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Админ-настройки модели Follow (подписки между пользователями)."""

    list_display = ('id', 'user', 'author')
    search_fields = (
        'user__username',
        'author__username',
        'user__email',
        'author__email',
    )
    list_select_related = ('user', 'author')
    ordering = ('id',)
