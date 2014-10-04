# -*- coding: utf-8 -*-
from collections import OrderedDict

from django.core.exceptions import PermissionDenied
from django.http.response import Http404
from django.utils.translation import ugettext as _

from rest_framework import status
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.views import exception_handler


class ErrorGroupEnum(object):
    """Enum for error groups."""
    VALIDATION_ERRORS = ('10', _(u'Model validation error.'))
    AUTHENTICATION_ERROR = ('20', u'Authentication error.')
    PERMISSION_ERROR = ('30', u'Permission error.')
    URL_ERROR = ('40', u'URL error.')
    SERVER_ERROR = ('50', u'Server error.')


class ValidationErrorEnum(object):
    """Enum for validation errors."""
    INVALID_FIELD = ('100', _(u'One or more fields are invalid.'))
    UNKNOWN_ERROR = ('198', _(u'Unknown error occurred.'))
    OTHER_ERROR = ('199', _(u'Other error occurred.'))


class AuthenticationErrorEnum(object):
    """Enum for authentication errors."""
    AUTHENTICATION_FAILED = ('100', _(u'Incorrect authentication credentials.'))
    NOT_AUTHENTICATED = ('101', _(u'Authentication credentials were not provided.'))


class PermissionErrorEnum(object):
    """Enum for permission errors."""
    PERMISSION_DENIED = ('100', _(u'You do not have permission to perform this action.'))


class UrlErrorEnum(object):
    """Enum for url errors."""
    NOT_ALLOWED = ('100', _(u'Method "%s" not allowed.'))
    NOT_FOUND = ('101', _(u'Not found.'))


class ServerErrorEnum(object):
    """Enum for server errors"""
    OTHER_ERROR = ('199', _(u'Other error occurred.'))


class ApiException(Exception):
    """Base class for api 2.0 exceptions."""

    status_code = None
    error_group = None

    def __init__(self, detail, rest_api_exception=None):
        if rest_api_exception:
            self.status_code = rest_api_exception.status_code
            self.auth_header = getattr(rest_api_exception, 'auth_header', None)
            self.wait = getattr(rest_api_exception, 'wait', None)

        code, description, detail = self.get_error(detail)
        group_code, group_description = self.error_group

        self.detail = OrderedDict()
        self.detail['message'] = group_description
        self.detail['code'] = group_code + code
        self.detail['description'] = description
        if detail:
            self.detail['errors'] = detail

    def get_error(self, detail):
        """Identify specific error.

        It should return error code, error description and may be some
        additional error information. By default this information is assumed
        to be sent directly.
        """
        return (
            detail.get('code', ''),
            detail.get('description', ''),
            detail.get('detail', None)
        )


class ValidationException(ApiException):
    """Raised on REST Framework validation errors."""
    status_code = status.HTTP_400_BAD_REQUEST
    error_group = ErrorGroupEnum.VALIDATION_ERRORS

    def get_error(self, detail):
        """Identify specific validation error."""
        if detail.get('non_field_errors'):
            error = ValidationErrorEnum.OTHER_ERROR
            error_detail = detail['non_field_errors']
        elif detail:
            error = ValidationErrorEnum.INVALID_FIELD
            detail.pop('non_field_errors', None)
            error_detail = detail
        else:
            error = ValidationErrorEnum.UNKNOWN_ERROR
            error_detail = {}
        return error[0], error[1], error_detail


class AuthenticationException(ApiException):
    """Raised on REST Framework authentication errors."""

    status_code = status.HTTP_401_UNAUTHORIZED
    error_group = ErrorGroupEnum.AUTHENTICATION_ERROR


class PermissionException(ApiException):
    """Raised on REST Framework permission errors."""

    status_code = status.HTTP_403_FORBIDDEN
    error_group = ErrorGroupEnum.PERMISSION_ERROR


class UrlException(ApiException):
    """Raised if url is invalid."""

    error_group = ErrorGroupEnum.URL_ERROR

    def __init__(self, detail, rest_api_exception=None):
        super(UrlException, self).__init__(detail, rest_api_exception)
        if self.detail['code'].endswith(UrlErrorEnum.NOT_ALLOWED[0]):
            self.status_code = status.HTTP_405_METHOD_NOT_ALLOWED
        elif self.detail['code'].endswith(UrlErrorEnum.NOT_FOUND[0]):
            self.status_code = status.HTTP_404_NOT_FOUND


class ServerException(ApiException):
    """Raised on REST Framework permission errors."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_group = ErrorGroupEnum.SERVER_ERROR


def api_exception_handler(exception):
    """Handler for exceptions being raised during work of REST API"""

    # Here we should convert REST Framework exceptions to our exceptions.
    if isinstance(exception, exceptions.APIException):
        if isinstance(exception, exceptions.AuthenticationFailed):
            error = AuthenticationErrorEnum.AUTHENTICATION_FAILED
            exception = AuthenticationException(
                {'code': error[0], 'description': error[1]}, exception)
        elif isinstance(exception, exceptions.NotAuthenticated):
            error = AuthenticationErrorEnum.NOT_AUTHENTICATED
            exception = AuthenticationException(
                {'code': error[0], 'description': error[1]}, exception)
        elif isinstance(exception, exceptions.PermissionDenied):
            error = PermissionErrorEnum.PERMISSION_DENIED
            exception = PermissionException(
                {'code': error[0], 'description': error[1]}, exception)
        elif isinstance(exception, exceptions.MethodNotAllowed):
            error = UrlErrorEnum.NOT_ALLOWED
            exception = UrlException(
                {'code': error[0], 'description': exception.detail},
                exception)
    # ... and also Django 404 exception
    elif isinstance(exception, Http404):
        error = UrlErrorEnum.NOT_FOUND
        exception = UrlException({'code': error[0], 'description': error[1]})
    # ... and also Django Permission Exception
    elif isinstance(exception, PermissionDenied):
        error = PermissionErrorEnum.PERMISSION_DENIED
        exception = PermissionException(
            {'code': error[0], 'description': error[1]})
    # ... and also any other not REST Framework exception
    elif not isinstance(exception, (exceptions.APIException, ApiException)):
        error = ServerErrorEnum.OTHER_ERROR
        exception = ServerException(
            {'code': error[0], 'description': error[1], 'detail': exception.message})

    if isinstance(exception, ApiException):
        # Response in the case of our exception to be caught is similar to
        # response in the case of standard REST Framework exception to
        # be caught. The only difference is JSON format.
        headers = {}
        if getattr(exception, 'auth_header', None):
            headers['WWW-Authenticate'] = exception.auth_header
        if getattr(exception, 'wait', None):
            headers['X-Throttle-Wait-Seconds'] = '%d' % exception.wait

        return Response(
            exception.detail, status=exception.status_code, headers=headers)
    else:
        return exception_handler(exception)
