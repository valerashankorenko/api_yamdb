from rest_framework import permissions


class IsReviewAuthor(permissions.IsAuthenticated):
    """
    Доступ разрешен только автору отзыва.
    """

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsModeratorOrAdmin(permissions.BasePermission):
    """
    Разрешает модераторам и администраторам редактировать
    и удалять чужие отзывы и комментарии.
    """

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and (
            request.user.is_moderator or request.user.is_admin
            or obj.author == request.user)


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
