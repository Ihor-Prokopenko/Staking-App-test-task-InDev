from django.urls import path, include
from staking_app import views


wallets = [
    path("wallets/", include([
        path("", views.WalletsAPIView.as_view(), name="wallets"),
        path("<int:pk>/", views.WalletDetailAPIView.as_view(), name="wallets_detail"),
        path("replenish/", views.WalletReplenishAPIView.as_view(), name="wallets_replenish"),
        path("withdraw/", views.WalletWithdrawAPIView.as_view(), name="wallets_withdraw"),
    ]))
]

positions = [
    path("positions/", include([
        path("", views.PositionsListAPIView.as_view(), name="positions"),
        path("create/", views.CreatePositionAPIView.as_view(), name="positions_create"),
        path("<int:pk>/", views.PositionDetailAPIView.as_view(), name="positions_detail"),
        path("<int:pk>/", views.PositionDetailAPIView.as_view(), name="positions_delete"),
        path("increase/<int:pk>/", views.PositionIncreaseAPIView.as_view(), name="positions_increase"),
        path("decrease/<int:pk>/", views.PositionDecreaseAPIView.as_view(), name="positions_decrease"),
    ]))
]

conditions = [
    path("conditions/", include([
        path("", views.ConditionsListAPIView.as_view(), name="conditions"),
        path("create/", views.ConditionsCreateAPIView.as_view(), name="conditions_create"),
        path("<int:pk>/", views.ConditionsDetailAPIView.as_view(), name="conditions_detail"),
        path("<int:pk>/", views.ConditionsDetailAPIView.as_view(), name="conditions_delete"),
    ]))
]

staking_pools = [
    path("pools/", include([
        path("", views.StackingPoolListAPIView.as_view(), name="pools"),
        path("create/", views.StackingPoolCreateAPIView.as_view(), name="pools_create"),
        path("<int:pk>/", views.StackingPoolDetailAPIView.as_view(), name="pools_detail"),
        path("<int:pk>/", views.StackingPoolDetailAPIView.as_view(), name="pools_delete"),
        path("edit/<int:pk>/", views.StackingPoolEditAPIView.as_view(), name="pools_edit"),
    ]))
]

urlpatterns = [] + wallets + positions + conditions + staking_pools
