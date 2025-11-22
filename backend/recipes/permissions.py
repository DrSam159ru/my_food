from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorOrReadOnly(BasePermission):
    """Разрешает изменение объекта только его автору, чтение — всем."""

    def has_permission(self, request, view):
        """
        Разрешает доступ к вьюсету для безопасных методов
        или аутентифицированных пользователей.
        """
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Разрешает доступ, если метод безопасный или пользователь — автор.
        """
        if request.method in SAFE_METHODS:
            return True
        return (
            getattr(obj, 'author_id', None)
            == getattr(request.user, 'id', None)
        )
