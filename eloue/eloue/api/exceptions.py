# coding=utf-8
from collections import OrderedDict
from django.utils.translation import ugettext as _
from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import exception_handler


class ErrorGroupEnum(object):
    """Enum for error groups."""
    VALIDATION_ERRORS = ('10', _(u'Model validation error.'))


class ValidationErrorEnum(object):
    """Enum for validation errors."""
    INVALID_FIELD = ('100', _(u'One or more fields are invalid.'))
    UNKNOWN_ERROR = ('198', _(u'Unknown error occurred.'))
    OTHER_ERROR = ('199', _(u'Other error occurred.'))


class ValidationExceptions(APIException):
    """Raised on REST Framework validation errors."""
    status_code = HTTP_400_BAD_REQUEST

    def __init__(self, detail):
        code, description, detail = self.get_error(detail)
        group_code, group_description = ErrorGroupEnum.VALIDATION_ERRORS

        self.detail = OrderedDict()
        self.detail['message'] = group_description
        self.detail['code'] = group_code + code
        self.detail['description'] = description
        self.detail['errors'] = detail

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


def api_exception_handler(exception):
    """Handler for exceptions being raised during work of REST API"""
    response = exception_handler(exception)
    return response
