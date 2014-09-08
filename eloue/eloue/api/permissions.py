# -*- coding: utf-8 -*-
from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS

class DefaultPermissions(permissions.DjangoModelPermissions):
    def has_permission(self, request, view):
        user = request.user
        if user:
            # we only check for Django Model Permissions for the team staff
            if user.is_staff and not user.is_superuser:
                return super(DefaultPermissions, self).has_permission(request, view)
            # we require authenticated user
            if user.is_authenticated():
                return True
        # disallow by default
        return False

class IsAuthenticatedOrReadOnly(DefaultPermissions):
    def has_permission(self, request, view):
        return (request.user.is_authenticated() and request.method in SAFE_METHODS or
            super(IsAuthenticatedOrReadOnly, self).has_permission(request, view)
        )

class IsStaffOrReadOnly(DefaultPermissions):
    def has_permission(self, request, view):
        return (request.user.is_authenticated() and request.method in SAFE_METHODS or
            request.user.is_staff or
            super(IsStaffOrReadOnly, self).has_permission(request, view)
        )

class UserPermissions(DefaultPermissions):
    def has_permission(self, request, view):
        # anonymous users should be allowed to POST /users/ for signing up
        return ((request.method in SAFE_METHODS if request.user.is_authenticated() else request.method == 'POST') or
            super(UserPermissions, self).has_permission(request, view)
        )

    def has_object_permission(self, request, view, obj):
        # allow write for himself
        return request.method in SAFE_METHODS or request.user == obj

class OwnerPermissions(IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        # allow editing for only owned products
        return request.method in SAFE_METHODS or request.user == getattr(obj, view.owner_field)
