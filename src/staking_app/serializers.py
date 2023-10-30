from rest_framework import serializers

from staking_app.models import UserWallet, UserPosition, StackingPool, PoolConditions
from staking_app.staking_exceptions import StackingPoolException, UserPositionException


class UserWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserWallet
        fields = ["user", "balance"]


class StackingPoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = StackingPool
        fields = ["id", "name", "conditions"]

    def create(self, validated_data):
        return StackingPool.objects.create(**validated_data)


class UpdateStackingPoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = StackingPool
        fields = ["name"]

    def update(self, instance, validated_data):
        if instance.name == validated_data.get("name"):
            raise StackingPoolException("Name must be different")
        instance.name = validated_data.get("name")
        instance.save()
        return instance


class PoolConditionsSerializer(serializers.ModelSerializer):
    min_amount = serializers.DecimalField(max_digits=20, decimal_places=10)
    max_amount = serializers.DecimalField(max_digits=20, decimal_places=10)

    class Meta:
        model = PoolConditions
        fields = ["id", "min_amount", "max_amount"]

    def create(self, validated_data):
        return PoolConditions.objects.create(**validated_data)


class WalletReplenishSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(max_digits=20, decimal_places=10)

    class Meta:
        model = UserWallet
        fields = ["amount"]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value

    def create(self, validated_data):
        user_wallet = UserWallet.objects.get(user=self.context.get("request").user)
        amount = validated_data.get("amount")
        user_wallet.replenish(amount)
        user_wallet.save()
        return user_wallet


class WalletWithdrawSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(max_digits=20, decimal_places=10)

    class Meta:
        model = UserWallet
        fields = ["amount"]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value

    def create(self, validated_data):
        user_wallet = UserWallet.objects.get(user=self.context.get("request").user)
        amount = validated_data.get("amount")
        user_wallet.withdraw(amount)
        user_wallet.save()
        return user_wallet


class CreatePositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPosition
        fields = ['pool', 'amount']

    def create(self, validated_data):
        user_position = UserPosition.objects.create(user=self.context.get("request").user, **validated_data)
        user_position.save()
        return user_position


class UserPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPosition
        fields = ["id", "user", "pool", "amount"]


class PositionIncreaseSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(max_digits=20, decimal_places=10, required=True)

    class Meta:
        model = UserPosition
        fields = ["amount"]

    def create(self, validated_data):
        user_position = UserPosition.objects.get(pk=self.context.get("pk"))
        amount = validated_data.get("amount")
        try:
            success = user_position.increase_position(amount)
            user_position.save()
        except UserPositionException as e:
            raise serializers.ValidationError({"message": str(e)})
        if not success:
            return False
        return user_position


class PositionDecreaseSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=20, decimal_places=10, required=True)

    class Meta:
        model = UserPosition
        fields = ["amount"]

    def create(self, validated_data):
        user_position = UserPosition.objects.get(pk=self.context.get("pk"))
        amount = validated_data.get("amount")
        try:
            success = user_position.decrease_position(amount)
            user_position.save()
        except UserPositionException as e:
            raise serializers.ValidationError({"message": str(e)})
        if not success:
            return False
        return user_position
