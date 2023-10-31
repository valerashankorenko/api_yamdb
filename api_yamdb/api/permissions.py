from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Доступ разрешен только автору объекта.
    """

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsAdmin(permissions.BasePermission):
    """
    Разрешение для аутентифицированного администратора/суперпользователя.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin or request.user.is_superuser)


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешен безопасные методы для всех пользователей.
    Все остальные методы только для Администратора и Суперюзера.
    """
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated
                and (request.user.is_admin or request.user.is_superuser)
                )
        )
