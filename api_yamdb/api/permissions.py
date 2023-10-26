from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Доступ разрешен только автору объекта.
    """

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
