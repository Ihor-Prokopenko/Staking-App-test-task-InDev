from django.urls import path, include

from users import views


auth = [
    path("register/", views.UserCreateAPIView.as_view(), name="register"),
]

urlpatterns = [] + auth
