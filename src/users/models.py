from django.db import models
from django.contrib.auth.models import AbstractUser

from users.utils import auto_create_wallet


class User(AbstractUser):
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.email}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        auto_create_wallet(self)
