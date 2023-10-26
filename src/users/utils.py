from rest_framework.exceptions import PermissionDenied
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, PermissionDenied):
        response.data = {"message": exc.detail}

    return response
