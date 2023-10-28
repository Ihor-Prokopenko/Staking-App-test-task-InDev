from django.db import models
from django.contrib.auth.models import User


class UserWallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=20, decimal_places=10)


class UserPosition(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pool = models.ForeignKey('StackingPool', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=10)


class StackingPool(models.Model):
    name = models.CharField(max_length=255)
    conditions = models.ForeignKey('PoolConditions', on_delete=models.CASCADE)


class PoolConditions(models.Model):
    min_amount = models.DecimalField(max_digits=20, decimal_places=10)
    max_amount = models.DecimalField(max_digits=20, decimal_places=10)


