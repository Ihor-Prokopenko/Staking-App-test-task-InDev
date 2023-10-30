from drf_yasg import openapi


replenish_withdraw_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'amount': openapi.Schema(
            type=openapi.TYPE_NUMBER,
            format=openapi.FORMAT_DECIMAL,
        ),
    },
    required=['amount'],
)

increase_decrease_position_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'amount': openapi.Schema(
            type=openapi.TYPE_NUMBER,
            format=openapi.FORMAT_DECIMAL,
        ),
    },
    required=['amount'],
)
