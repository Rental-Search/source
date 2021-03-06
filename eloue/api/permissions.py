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

            # check for public access if set for the view
            else:
                return view.public_mode

        # can't make a decision; pass to other permission checkers if there any, otherwise deny access
        return None


class PublicAccessPermission(permissions.DjangoModelPermissions):
    def has_permission(self, request, view):
        return request.user.is_authenticated() or view.public_mode


class IsAuthenticatedOrReadOnly(DefaultPermissions):
    def has_permission(self, request, view):
        if request.user.is_anonymous():
            return request.method in SAFE_METHODS
        return super(IsAuthenticatedOrReadOnly, self).has_permission(request, view)

class IsStaffOrReadOnly(DefaultPermissions):
    def has_permission(self, request, view):
        if request.user.is_anonymous() or (not request.user.is_staff and not request.user.is_superuser):
            return request.method in SAFE_METHODS
        return super(IsStaffOrReadOnly, self).has_permission(request, view)

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
        owner_fields = view.owner_field
        if isinstance(owner_fields, basestring):
            owner_fields = [owner_fields]
        return request.method in SAFE_METHODS or any(request.user == getattr(obj, owner_field) for owner_field in owner_fields)
