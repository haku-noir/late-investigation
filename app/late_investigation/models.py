from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime

dt_now_jst = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))

class Route(models.Model):
    name = models.CharField(max_length=70)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    number = models.PositiveSmallIntegerField("number", default=9999)
    is_teacher = models.BooleanField("is_teacher", default=False)
    routes = models.ManyToManyField(Route, blank=True)

class Delay(models.Model):
    year = models.PositiveSmallIntegerField(default=dt_now_jst.year)
    month = models.PositiveSmallIntegerField(default=dt_now_jst.month)
    day = models.PositiveSmallIntegerField(default=dt_now_jst.day)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    users = models.ManyToManyField(CustomUser, through="UserDelay")

class UserDelay(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    delay = models.ForeignKey(Delay, on_delete=models.CASCADE)
    is_checked = models.BooleanField(default=False)
    is_finished = models.BooleanField(default=False)
