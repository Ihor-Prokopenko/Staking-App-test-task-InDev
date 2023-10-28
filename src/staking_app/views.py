from django.shortcuts import render
from rest_framework import status, permissions
from rest_framework.generics import ListAPIView, GenericAPIView, CreateAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from staking_app.models import UserWallet, UserPosition, PoolConditions, StackingPool
from staking_app.serializers import UserWalletSerializer, StackingPoolSerializer, \
    PoolConditionsSerializer, WalletReplenishSerializer, WalletWithdrawSerializer, CreatePositionSerializer, \
    UserPositionSerializer, UpdateStackingPoolSerializer
from staking_app.staking_exceptions import UserPositionException, PoolConditionsException, StackingPoolException
from users.models import User
from users.user_permissions import OwnOrAdminPermission


class WalletsAPIView(ListAPIView):
    queryset = UserWallet.objects.all()
    serializer_class = UserWalletSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class WalletDetailAPIView(GenericAPIView):
    serializer_class = UserWalletSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get(self, request, pk):
        user = User.objects.filter(pk=pk).first()

        if not user:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        wallet = user.wallet
        serializer = self.get_serializer(wallet)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WalletReplenishAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = WalletReplenishSerializer(data=request.data, context={"request": request})

        if not serializer.is_valid():
            return Response({"message": serializer.errors},
                            status=status.HTTP_412_PRECONDITION_FAILED)

        wallet = serializer.save()
        return Response(
            {"message": f"Wallet replenished. Total amount: {wallet.balance}"}, status=status.HTTP_200_OK)


class WalletWithdrawAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = WalletWithdrawSerializer(data=request.data, context={"request": request})

        if not serializer.is_valid():
            return Response({"message": serializer.errors}, status=status.HTTP_412_PRECONDITION_FAILED)

        wallet = serializer.save()
        return Response(
            {"message": f"Wallet withdrawn. Total amount: {wallet.balance}"}, status=status.HTTP_200_OK
        )


class CreatePositionAPIView(CreateAPIView):
    serializer_class = CreatePositionSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return Response({"message": serializer.errors}, status=status.HTTP_412_PRECONDITION_FAILED)
        try:
            self.perform_create(serializer)
        except UserPositionException as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        headers = self.get_success_headers(serializer.data)
        return Response({"message": serializer.data}, status=status.HTTP_201_CREATED, headers=headers)


class PositionsListAPIView(ListAPIView):
    queryset = UserPosition.objects.all()
    serializer_class = UserPositionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = User.objects.filter(pk=self.request.user.id).first()
        if not user:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(user.positions.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PositionDetailAPIView(GenericAPIView):
    serializer_class = UserPositionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        position = UserPosition.objects.filter(pk=pk).first()
        if not position:
            return Response({"message": "Position not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(position)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        position = UserPosition.objects.filter(pk=pk).first()
        if request.user.id != position.user.id or not request.user.is_staff:
            return Response({"message": "Position not found"}, status=status.HTTP_404_NOT_FOUND)
        if not position:
            return Response({"message": "Position not found"}, status=status.HTTP_404_NOT_FOUND)
        deleted_count, data = position.delete()
        if not deleted_count:
            return Response({"message": "Position has not been deleted"}, status=status.HTTP_417_EXPECTATION_FAILED)
        return Response({"message": f"Position(id={pk}) was deleted successfully"}, status=status.HTTP_200_OK)


class PositionIncreaseAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        position = UserPosition.objects.filter(pk=pk).first()
        if not position:
            return Response({"message": "Position not found"}, status=status.HTTP_404_NOT_FOUND)
        if request.user.id != position.user.id:
            return Response({"message": "Position not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            success = position.increase_position(request.data.get("amount"))
        except UserPositionException as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        if not success:
            return Response({"message": "Position were not increased"}, status=status.HTTP_404_NOT_FOUND)
        return Response(
            {"message": f"Position increased. Total amount: {position.amount}"}, status=status.HTTP_200_OK)


class PositionDecreaseAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        position = UserPosition.objects.filter(pk=pk).first()
        if not position:
            return Response({"message": "Position not found"}, status=status.HTTP_404_NOT_FOUND)
        if request.user.id != position.user.id:
            return Response({"message": "Position not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            success = position.decrease_position(request.data.get("amount"))
        except UserPositionException as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        if not success:
            return Response({"message": "Position were not decreased"}, status=status.HTTP_404_NOT_FOUND)
        return Response(
            {"message": f"Position decreased. Total amount: {position.amount}"}, status=status.HTTP_200_OK
        )


class ConditionsListAPIView(ListAPIView):
    queryset = PoolConditions.objects.all()
    serializer_class = PoolConditionsSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ConditionsCreateAPIView(CreateAPIView):
    serializer_class = PoolConditionsSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({"message": serializer.errors}, status=status.HTTP_412_PRECONDITION_FAILED)
        try:
            self.perform_create(serializer)
        except PoolConditionsException as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        headers = self.get_success_headers(serializer.data)
        return Response({"message": serializer.data}, status=status.HTTP_201_CREATED, headers=headers)


class ConditionsDetailAPIView(GenericAPIView):
    serializer_class = PoolConditionsSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get(self, request, pk):
        conditions = PoolConditions.objects.filter(pk=pk).first()
        if not conditions:
            return Response({"message": "Conditions not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(conditions)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        conditions = PoolConditions.objects.filter(pk=pk).first()
        if not conditions:
            return Response({"message": "Conditions not found"}, status=status.HTTP_404_NOT_FOUND)
        deleted_count, data = conditions.delete()
        if not deleted_count:
            return Response(
                {"message": "Conditions has not been deleted"},
                status=status.HTTP_417_EXPECTATION_FAILED)
        return Response({"message": f"Conditions(id={pk}) was deleted successfully"}, status=status.HTTP_200_OK)


class StackingPoolListAPIView(ListAPIView):
    queryset = StackingPool.objects.all()
    serializer_class = StackingPoolSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class StackingPoolCreateAPIView(CreateAPIView):
    serializer_class = StackingPoolSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({"message": serializer.errors}, status=status.HTTP_412_PRECONDITION_FAILED)
        try:
            self.perform_create(serializer)
        except StackingPoolException as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        headers = self.get_success_headers(serializer.data)
        return Response({"message": serializer.data}, status=status.HTTP_201_CREATED, headers=headers)


class StackingPoolDetailAPIView(GenericAPIView):
    serializer_class = StackingPoolSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get(self, request, pk):
        stacking_pool = StackingPool.objects.filter(pk=pk).first()
        if not stacking_pool:
            return Response({"message": "Stacking pool not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(stacking_pool)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        stacking_pool = StackingPool.objects.filter(pk=pk).first()
        if not stacking_pool:
            return Response({"message": "Stacking pool not found"}, status=status.HTTP_404_NOT_FOUND)
        deleted_count, data = stacking_pool.delete()
        if not deleted_count:
            return Response(
                {"message": "Stacking pool has not been deleted"},
                status=status.HTTP_417_EXPECTATION_FAILED)
        return Response(
            {"message": f"Stacking pool(id={pk}) was deleted successfully"},
            status=status.HTTP_200_OK)


class StackingPoolEditAPIView(UpdateAPIView):
    queryset = StackingPool.objects.all()
    serializer_class = UpdateStackingPoolSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def update(self, request, pk):
        stacking_pool = self.get_queryset().filter(pk=pk).first()
        if not stacking_pool:
            return Response({"message": "Stacking pool not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(stacking_pool, data=request.data)
        if not serializer.is_valid():
            return Response({"message": serializer.errors}, status=status.HTTP_412_PRECONDITION_FAILED)
        try:
            self.perform_update(serializer)
        except StackingPoolException as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": serializer.data}, status=status.HTTP_200_OK)
