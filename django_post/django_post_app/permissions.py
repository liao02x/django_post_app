from rest_framework import permissions

class UserViewSetPermissions(permissions.BasePermission):
    def has_permission(self, request, view,):
        if request.user.is_superuser:
            return True
        
        if not request.user.is_authenticated:
            if view.action == 'create':
                return True
            else:
                return False
            
        if view.action == 'list':
            return False
        else:
            return True
        
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        return obj == request.user

class PostViewSetPermissions(permissions.BasePermission):
    def has_permission(self, request, view,):
        if request.user.is_superuser:
            return True
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if not request.user.is_authenticated:
            return False
        
        return True
        
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if view.action == 'partial_update':
            return True
        
        return obj.author == request.user
