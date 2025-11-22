from rest_framework import permissions


class AuthorOrReadOnly(permissions.BasePermission):
    """Разрешает изменение объекта только его автору, чтение — всем."""

    def has_permission(self, request, view):
        """
        Разрешает доступ, если метод безопасный
        или пользователь аутентифицирован.
        """
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        """
        Разрешает изменение объекта, если пользователь является его автором.
        """
        return (
            request.method in permissions.SAFE_METHODS
            or getattr(obj, 'author_id', None)
            == getattr(request.user, 'id', None)
        )
