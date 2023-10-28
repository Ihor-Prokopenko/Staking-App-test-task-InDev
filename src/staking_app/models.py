from django.db import models

from staking_app.staking_exceptions import UserPositionException, PoolConditionsException


class UserWallet(models.Model):
    user = models.OneToOneField("users.User", on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(max_digits=20, decimal_places=10, default=0)

    def __str__(self):
        return f"Wallet of {self.user}"

    def replenish(self, amount):
        self.balance += amount
        self.save()

    def withdraw(self, amount):
        self.balance -= amount
        self.save()


class UserPosition(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="positions")
    pool = models.ForeignKey('StackingPool', on_delete=models.CASCADE, related_name="positions")
    amount = models.DecimalField(max_digits=20, decimal_places=10)

    def __str__(self):
        return f"{self.user} - {self.pool}"

    def save(self, *args, **kwargs):
        if self.amount > self.pool.conditions.max_amount:
            raise UserPositionException(f"Amount too large. Max amount is {self.pool.conditions.max_amount}")
        if self.amount < self.pool.conditions.min_amount:
            raise UserPositionException(f"Amount too small. Min amount is {self.pool.conditions.min_amount}")

        if not self.pk:  # check if this is a new position, then withdraw the amount
            # user = self.user
            if self.user.wallet.balance < self.amount:
                raise UserPositionException(f"User balance too low. User balance is {user.wallet.balance}")
            self.user.wallet.withdraw(self.amount)
        super().save(*args, **kwargs)

    def calculate_profit(self):
        pass

    def increase_position(self, amount):
        if amount <= 0:
            raise UserPositionException("Amount to increase must be greater than 0")
        if (amount + self.amount) > self.pool.conditions.max_amount:
            raise UserPositionException(f"Effective amount too large. Max amount is {self.pool.conditions.max_amount}")
        if (amount + self.amount) < self.pool.conditions.min_amount:
            raise UserPositionException(f"Effective amount too small. Min amount is {self.pool.conditions.min_amount}")
        user = self.user
        if user.wallet.balance < self.amount:
            raise UserPositionException(f"User balance too low. User balance is {user.wallet.balance}")
        self.user.wallet.withdraw(amount)
        self.amount += amount
        self.save()
        return True

    def decrease_position(self, amount):
        if amount <= 0:
            raise UserPositionException("Amount to decrease must be greater than 0")
        if (self.amount - amount) < self.pool.conditions.min_amount:
            raise UserPositionException(
                f"Effective amount too small. Min amount is {self.pool.conditions.min_amount}")
        if (self.amount + amount) > self.pool.conditions.max_amount:
            raise UserPositionException(
                f"Effective amount too large. Max amount is {self.pool.conditions.max_amount}")

        self.user.wallet.replenish(amount)
        self.amount -= amount
        self.save()
        return True

    def delete(self, using=None, keep_parents=False):
        self.user.wallet.replenish(self.amount)
        return super().delete()

    def check_blockchain_status(self):
        pass


class StackingPool(models.Model):
    name = models.CharField(max_length=255, unique=True)
    conditions = models.ForeignKey('PoolConditions', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} | {str(self.conditions)}"


class PoolConditions(models.Model):
    min_amount = models.DecimalField(max_digits=20, decimal_places=10)
    max_amount = models.DecimalField(max_digits=20, decimal_places=10)

    def __str__(self):
        return f"{self.min_amount} - {self.max_amount}"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.max_amount <= self.min_amount:
            raise PoolConditionsException(f"Max amount must be greater than min amount")
        if self.min_amount <= 0:
            raise PoolConditionsException(f"Min amount must be greater than 0")
        if self.max_amount <= 0:
            raise PoolConditionsException(f"Max amount must be greater than 0")
        if PoolConditions.objects.filter(
                min_amount=self.min_amount,
                max_amount=self.max_amount).exclude(pk=self.pk).exists():
            raise PoolConditionsException("Pool Conditions with these values already exist")
        super().save()
