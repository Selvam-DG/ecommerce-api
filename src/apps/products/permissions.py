from rest_framework import permissions


class IsAdminOrVendor(permissions.BasePermission):
    """
    Custom permission to only allow admins or vendors to edit products.
    Vendors can only edit their own products.
    """
    
    def has_permission(self, request, view):
        """Check if user is authenticated and is admin or vendor."""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user can modify this specific product."""
        # Admins can modify any product
        if request.user.is_staff:
            return True
        
        # Vendors can only modify their own products
        if request.user.role == 'vendor':
            return obj.created_by == request.user
        
        return False