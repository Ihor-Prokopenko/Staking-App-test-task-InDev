from django.urls import path, include

from users import views


crud = [
    path("", views.UserListAPIView.as_view(), name="user_list"),
    path("register/", views.UserCreateAPIView.as_view(), name="register"),
]

urlpatterns = [] + crud
