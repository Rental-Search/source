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
            elif user.is_authenticated():
                return True
            elif hasattr(view, 'public_methods'):
                is_public_method = view.action in view.public_methods
                is_public_search = (
                    request.method == 'GET' and
                    view.action == 'list' and
                    request.QUERY_PARAMS and
                    'search' in view.public_methods)

                if is_public_method or is_public_search:
                    return True
                else:
                    return False
        # can't make decision
        return None

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

class IsOwnerOrReadOnly(IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        # allow editing for only owned products
        owner_field = view.owner_field
        if not isinstance(owner_field, basestring):
            owner_field = iter(owner_field).next()
        return request.method in SAFE_METHODS or request.user == getattr(obj, owner_field)
