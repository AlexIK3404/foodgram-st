from rest_framework import permissions


class IsAuthorOrReadOnlyPermission(permissions.BasePermission):
    """
    Разрешает только авторам изменять или удалять объект.
    Остальным разрешён только просмотр (GET, HEAD, OPTIONS).
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
