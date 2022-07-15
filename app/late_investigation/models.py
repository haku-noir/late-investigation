from django.contrib.auth.models import AbstractUser
from django.db import models
class CustomUser(AbstractUser):
    number = models.PositiveSmallIntegerField("number", default=0)
    is_teacher = models.BooleanField("is_teacher", default=False)
    is_active = models.BooleanField("is_active", default=True)

class Route(models.Model):
    name = models.CharField(max_length=70)

class UserRoute(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    route = models.OneToOneField(Route, on_delete=models.CASCADE)
