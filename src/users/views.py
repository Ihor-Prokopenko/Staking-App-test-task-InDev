from django.contrib.auth import logout
from django.contrib.auth.hashers import check_password, make_password
from rest_framework import status, filters, permissions, mixins
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, ListAPIView, GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from users.models import User
from users.serializers import UserSerializer, UserEditSerializer, ChangePasswordSerializer
from users.user_permissions import OwnOrAdminPermission


class UserCreateAPIView(CreateAPIView):
    serializer_class = UserSerializer
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            field, message = (list(e.detail.keys())[0], list(e.detail.values())[0][0])
            message = f"{field}: {message}"
            status_code = status.HTTP_400_BAD_REQUEST
        else:
            validated_data = serializer.validated_data
            password = validated_data.get("password")
            hashed_password = make_password(password)
            serializer.validated_data["password"] = hashed_password
            serializer.save()

            message = f"Registration successful"
            status_code = status.HTTP_201_CREATED

        return Response({"message": message}, status=status_code)


class UserListAPIView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ["get"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["username", "email"]
    ordering_fields = "__all__"

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response_data = {
                "pages": (queryset.count() + self.pagination_class.page_size - 1) // self.pagination_class.page_size,
                "data": serializer.data,
            }
            return Response(response_data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserDetailAPIView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, OwnOrAdminPermission]
    http_method_names = ["get"]

    def get(self, request, pk):
        user = User.objects.filter(pk=pk).first()
        if not user:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DeleteUserAPIView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, OwnOrAdminPermission]
    http_method_names = ["delete"]

    def delete(self, request: Request, pk):
        user = User.objects.filter(pk=pk).first()
        if not user:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        deleted_count, data = user.delete()
        if not deleted_count:
            return Response({"message": "User has not been deleted"}, status=status.HTTP_417_EXPECTATION_FAILED)

        return Response({"message": f"User(id={pk}) was deleted successfully"}, status=status.HTTP_200_OK)


class UserEditAPIView(mixins.UpdateModelMixin, GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserEditSerializer
    http_method_names = ["put"]
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):
        partial = True
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=partial)

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            field, message = (list(e.detail.keys())[0], list(e.detail.values())[0][0])
            message = f"{field}: {message}"
            status_code = status.HTTP_400_BAD_REQUEST
        else:
            try:
                self.perform_update(serializer)
            except Exception:
                return Response(
                    {"message": "User data has not been updated"},
                    status=status.HTTP_417_EXPECTATION_FAILED
                )

            message = "User details updated"
            status_code = status.HTTP_200_OK

        return Response({"message": message}, status=status_code)


class UserChangePasswordAPIView(mixins.UpdateModelMixin, GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["put"]

    def put(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            return Response({"message": str(e)}, status=status.HTTP_412_PRECONDITION_FAILED)

        old_password = serializer.validated_data.get("old_password")
        new_password = serializer.validated_data.get("new_password")
        confirm_password = serializer.validated_data.get("confirm_password")

        if new_password == old_password:
            return Response(
                {"message": "New password must be different from old password"},
                status=status.HTTP_412_PRECONDITION_FAILED,
            )

        if not check_password(old_password, user.password):
            return Response({"message": "Invalid old password"}, status=status.HTTP_412_PRECONDITION_FAILED)

        if new_password != confirm_password:
            return Response({"message": "Password mismatch"}, status=status.HTTP_412_PRECONDITION_FAILED)

        try:
            user.set_password(new_password)
            user.save()
        except Exception:
            return Response(
                {"message": "Password has not been changed"},
                status=status.HTTP_417_EXPECTATION_FAILED
                )

        logout(request)
        return Response(
            {"message": "Password changed successfully. You can login now."},
            status=status.HTTP_200_OK
            )

