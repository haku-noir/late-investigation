from django.contrib.auth.models import AbstractUser
from django.db import models
class CustomUser(AbstractUser):
    is_teacher = models.BooleanField("is_teacher", default=False)
    is_active = models.BooleanField("is_active", default=True)
