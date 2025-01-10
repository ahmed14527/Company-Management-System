from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    Custom permission to only allow Admins to access the view.
    """
    def has_permission(self, request, view):
        # Check if the user is authenticated and has the 'Admin' role
        return request.user.is_authenticated and request.user.role == 'Admin'


class IsManager(permissions.BasePermission):
    """
    Custom permission to allow Admins and Managers to access the view.
    """
    def has_permission(self, request, view):
        # Check if the user is authenticated and has the 'Admin' or 'Manager' role
        return request.user.is_authenticated and request.user.role in ['Admin', 'Manager']


class IsEmployee(permissions.BasePermission):
    """
    Custom permission to allow Admins, Managers, and Employees to access the view.
    """
    def has_permission(self, request, view):
        # Check if the user is authenticated and has the 'Admin', 'Manager', or 'Employee' role
        return request.user.is_authenticated and request.user.role in ['Admin', 'Manager', 'Employee']
