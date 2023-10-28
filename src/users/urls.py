from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

from users import views


crud = [
    path("", views.UserListAPIView.as_view(), name="user_list"),
    path("<int:pk>/", views.UserDetailAPIView.as_view(), name="user_detail"),
    path("register/", views.UserCreateAPIView.as_view(), name="register"),
    path("delete/<int:pk>/", views.DeleteUserAPIView.as_view(), name="delete_user"),
    path("edit-profile/", views.UserEditAPIView.as_view(), name="edit_profile"),
    path("change-password/", views.UserChangePasswordAPIView.as_view(), name="change_password"),
]

auth = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
]

urlpatterns = [] + crud + auth
