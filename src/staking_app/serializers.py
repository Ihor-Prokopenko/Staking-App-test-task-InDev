from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from staking_app.models import UserWallet, UserPosition, StackingPool, PoolConditions
from staking_app.staking_exceptions import StackingPoolException


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

    def create(self, validated_data):
        user_wallet = UserWallet.objects.get(user=self.context.get("request").user)
        user_wallet.replenish(validated_data.get("amount"))
        user_wallet.save()
        return user_wallet


class WalletWithdrawSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(max_digits=20, decimal_places=10)

    class Meta:
        model = UserWallet
        fields = ["amount"]

    def create(self, validated_data):
        user_wallet = UserWallet.objects.get(user=self.context.get("request").user)
        user_wallet.withdraw(validated_data.get("amount"))
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
    class Meta:
        model = UserPosition
        fields = ["amount"]

