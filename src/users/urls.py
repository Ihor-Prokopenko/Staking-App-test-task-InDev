from django.urls import path, include

from users import views


crud = [
    path("", views.UserListAPIView.as_view(), name="user_list"),
    path("register/", views.UserCreateAPIView.as_view(), name="register"),
    path("delete/<int:pk>/", views.DeleteUserAPIView.as_view(), name="delete_user"),
    path("edit-profile/", views.UserEditView.as_view(), name="edit_profile"),
]

urlpatterns = [] + crud
