from rest_framework import permissions


class IsModeratorOrAdmin(permissions.BasePermission):
    """
    Разрешение авторам редактировать и удалять свои отзывы и комментарии,
    а модераторам, администраторам и суперпользователям редактировать
    и удалять чужие отзывы и комментарии.
    """

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and (
            request.user.is_moderator or request.user.is_admin
            or request.user.is_superuser or obj.author == request.user)


class IsAdmin(permissions.BasePermission):
    """
    Разрешение для аутентифицированного администратора/суперпользователя.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin or request.user.is_superuser)


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешены безопасные методы для всех пользователей.
    Все остальные методы только для Администратора и Суперюзера.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated
                and (request.user.is_admin or request.user.is_superuser)
                )
        )
