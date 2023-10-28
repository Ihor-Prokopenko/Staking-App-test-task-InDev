from rest_framework.exceptions import PermissionDenied
from rest_framework.views import exception_handler

from staking_app.models import UserWallet


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, PermissionDenied):
        response.data = {"message": exc.detail}

    return response


def auto_create_wallet(user):
    user_wallet = UserWallet.objects.get_or_create(user=user)[0]
    return user_wallet
