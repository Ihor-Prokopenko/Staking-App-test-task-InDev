from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, permissions
from rest_framework.generics import ListAPIView, GenericAPIView, CreateAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from staking_app.models import UserWallet, UserPosition, PoolConditions, StackingPool
from staking_app import serializers as staking_app_serializers
from staking_app.staking_exceptions import UserPositionException, PoolConditionsException, StackingPoolException
from users.models import User
from staking_app import swagger_schemas


class WalletsAPIView(ListAPIView):
    queryset = UserWallet.objects.all()
    serializer_class = staking_app_serializers.UserWalletSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class WalletDetailAPIView(GenericAPIView):
    serializer_class = staking_app_serializers.UserWalletSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get(self, request, pk):
        """
        Get the user wallet by its primary key.

        Args:
            request (HttpRequest): The HTTP request object.
            pk (int): The primary key of the user wallet.

        Returns:
            Response: The HTTP response containing the serialized user wallet data.

        Raises:
            status.HTTP_404_NOT_FOUND: If the wallet is not found.
        """
        wallet = UserWallet.objects.filter(pk=pk).first()

        if not wallet:
            return Response({"message": "Wallet not found"}, status=status.HTTP_404_NOT_FOUND)
        if wallet.user.id != request.user.id:
            if not request.user.is_staff:
                return Response({"message": "Wallet not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(wallet)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WalletReplenishAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(request_body=swagger_schemas.replenish_withdraw_schema)
    def post(self, request, *args, **kwargs):
        """
        Provide a replenish of the user wallet.

        Parameters:
            request (HttpRequest): The HTTP request object.
            request['data']['amount']: The amount to replenish.

        Returns:
            Response: The HTTP response object with the result of the operation.
        """
        serializer = staking_app_serializers.WalletReplenishSerializer(data=request.data, context={"request": request})

        if not serializer.is_valid():
            return Response({"message": serializer.errors},
                            status=status.HTTP_412_PRECONDITION_FAILED)

        wallet = serializer.save()
        return Response(
            {"message": f"Wallet replenished. Total amount: {wallet.balance}"}, status=status.HTTP_200_OK)


class WalletWithdrawAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(request_body=swagger_schemas.replenish_withdraw_schema)
    def post(self, request, *args, **kwargs):
        """
        Provide a withdrawal of the user wallet.

        Parameters:
            request (HttpRequest): The HTTP request object.
            request['data']['amount']: The amount to withdraw.

        Returns:
            Response: The HTTP response object with the result of the operation.
        """
        serializer = staking_app_serializers.WalletWithdrawSerializer(data=request.data, context={"request": request})

        if not serializer.is_valid():
            return Response({"message": serializer.errors}, status=status.HTTP_412_PRECONDITION_FAILED)

        wallet = serializer.save()
        return Response(
            {"message": f"Wallet withdrawn. Total amount: {wallet.balance}"}, status=status.HTTP_200_OK
        )


class CreatePositionAPIView(CreateAPIView):
    serializer_class = staking_app_serializers.CreatePositionSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        """
        Create a position.

        Parameters:
            request (HttpRequest): The HTTP request object.
            request['data']['pool']: The pool address.
            request['data']['amount']: The amount to add.

        Returns:
            Response: The HTTP response object with the result of the operation.
        """
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
    serializer_class = staking_app_serializers.UserPositionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Get the positions list of the user.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            Response: The HTTP response containing the serialized positions list.
        """
        user = User.objects.filter(pk=self.request.user.id).first()
        if not user:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(user.positions.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PositionDetailAPIView(GenericAPIView):
    serializer_class = staking_app_serializers.UserPositionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        """
        Get a position detail by its primary key.

        Args:
            request (HttpRequest): The HTTP request object.
            pk (str): The primary key of the position.

        Returns:
            Response: The HTTP response containing the serialized position.
        """
        position = UserPosition.objects.filter(pk=pk).first()
        if not position:
            return Response({"message": "Position not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(position)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        """
        Delete a position.

        Args:
            request (HttpRequest): The HTTP request object.
            pk (str): The primary key of the position.

        Returns:
            Response: The HTTP response object with the result of the operation.
        """
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

    @swagger_auto_schema(request_body=swagger_schemas.increase_decrease_position_schema)
    def post(self, request, pk):
        """
        Increase a position by a given amount.

        Args:
            request (HttpRequest): The HTTP request object.
            pk (str): The primary key of the position.
            request['data']['amount']: The amount to increase.

        Returns:
            Response: The HTTP response object with the result of the operation.
        """
        position = UserPosition.objects.filter(pk=pk).first()
        if not position:
            return Response({"message": "Position not found"}, status=status.HTTP_404_NOT_FOUND)
        if request.user.id != position.user.id:
            return Response({"message": "Position not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = staking_app_serializers.PositionIncreaseSerializer(data=request.data, context={"pk": pk})
        if not serializer.is_valid():
            return Response({"message": serializer.errors}, status=status.HTTP_412_PRECONDITION_FAILED)

        updated_obj = serializer.save()

        if not updated_obj:
            return Response({"message": "Position were not increased"}, status=status.HTTP_404_NOT_FOUND)
        return Response(
            {"message": f"Position increased. Total amount: {updated_obj.amount}"}, status=status.HTTP_200_OK)


class PositionDecreaseAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(request_body=swagger_schemas.increase_decrease_position_schema)
    def post(self, request, pk):
        """
        Decrease a position by a given amount.

        Args:
            request (HttpRequest): The HTTP request object.
            pk (str): The primary key of the position.
            request['data']['amount']: The amount to decrease.

        Returns:
            Response: The HTTP response object with the result of the operation.
        """
        position = UserPosition.objects.filter(pk=pk).first()
        if not position:
            return Response({"message": "Position not found"}, status=status.HTTP_404_NOT_FOUND)
        if request.user.id != position.user.id:
            return Response({"message": "Position not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = staking_app_serializers.PositionDecreaseSerializer(data=request.data, context={"pk": pk})
        if not serializer.is_valid():
            return Response({"message": serializer.errors}, status=status.HTTP_412_PRECONDITION_FAILED)

        updated_obj = serializer.save()

        if not updated_obj:
            return Response({"message": "Position were not decreased"}, status=status.HTTP_404_NOT_FOUND)
        return Response(
            {"message": f"Position decreased. Total amount: {updated_obj.amount}"}, status=status.HTTP_200_OK
        )


class ConditionsListAPIView(ListAPIView):
    queryset = PoolConditions.objects.all()
    serializer_class = staking_app_serializers.PoolConditionsSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        """
        Get all conditions.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            Response: The HTTP response containing the serialized conditions list.
        """
        return self.list(request, *args, **kwargs)


class ConditionsCreateAPIView(CreateAPIView):
    serializer_class = staking_app_serializers.PoolConditionsSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def create(self, request, *args, **kwargs):
        """
        Create a new condition.

        Args:
            request (HttpRequest): The HTTP request object.
            request['data']['minimum_amount']: The minimum amount.
            request['data']['maximum_amount']: The maximum amount.

        Returns:
            Response: The HTTP response object with the result of the operation.
        """
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
    serializer_class = staking_app_serializers.PoolConditionsSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get(self, request, pk):
        """
        Get a condition.

        Args:
            request (HttpRequest): The HTTP request object.
            pk (str): The primary key of the condition.

        Returns:
            Response: The HTTP response containing the serialized condition.
        """
        conditions = PoolConditions.objects.filter(pk=pk).first()
        if not conditions:
            return Response({"message": "Conditions not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(conditions)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        """
        Delete a condition.

        Args:
            request (HttpRequest): The HTTP request object.
            pk (str): The primary key of the condition.

        Returns:
            Response: The HTTP response object with the result of the operation.
        """
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
    serializer_class = staking_app_serializers.StackingPoolSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        """
        Get all stacking pools.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            Response: The HTTP response containing the serialized stacking pools list.
        """
        return self.list(request, *args, **kwargs)


class StackingPoolCreateAPIView(CreateAPIView):
    serializer_class = staking_app_serializers.StackingPoolSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def create(self, request, *args, **kwargs):
        """
        Create a new stacking pool.

        Args:
            request (HttpRequest): The HTTP request object.
            request['data']['name']: The name of the stacking pool.
            request['data']['conditions']: The id of conditions.

        Returns:
            Response: The HTTP response object with the result of the operation.
        """
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
    serializer_class = staking_app_serializers.StackingPoolSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get(self, request, pk):
        """
        Get a stacking pool.

        Args:
            request (HttpRequest): The HTTP request object.
            pk (str): The primary key of the stacking pool.

        Returns:
            Response: The HTTP response containing the serialized stacking pool.
        """
        stacking_pool = StackingPool.objects.filter(pk=pk).first()
        if not stacking_pool:
            return Response({"message": "Stacking pool not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(stacking_pool)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        """
        Delete a stacking pool.

        Args:
            request (HttpRequest): The HTTP request object.
            pk (str): The primary key of the stacking pool.

        Returns:
            Response: The HTTP response object with the result of the operation.
        """
        stacking_pool = StackingPool.objects.filter(pk=pk).first()
        if not stacking_pool:
            return Response({"message": "Stacking pool not found"}, status=status.HTTP_404_NOT_FOUND)
        for position in stacking_pool.positions.all():
            position.money_back()
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
    serializer_class = staking_app_serializers.UpdateStackingPoolSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def update(self, request, pk):
        """
        Update a stacking pool.

        Args:
            request (HttpRequest): The HTTP request object.
            pk (str): The primary key of the stacking pool.
            request['data']['name']: The name of the stacking pool.

        Returns:
            Response: The HTTP response object with the result of the operation.
        """
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
