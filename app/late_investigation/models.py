from django.contrib.auth.models import AbstractUser
from django.db import models

class Route(models.Model):
    name = models.CharField(max_length=70)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    number = models.PositiveSmallIntegerField("number", default=0)
    is_teacher = models.BooleanField("is_teacher", default=False)
    is_active = models.BooleanField("is_active", default=True)
    route = models.ManyToManyField(Route, blank=True)
