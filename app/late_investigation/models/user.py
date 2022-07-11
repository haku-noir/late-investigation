from django.db import models
from .model import Model

class Sex(Model):
    name = models.CharField(max_length=50)

class User(Model):
    name = models.CharField(max_length=20)
    email = models.CharField(max_length=50)
    sex_key = models.ForeignKey(Sex, on_delete=models.PROTECT)

class Teacher(Model):
    user_key = models.ForeignKey(User, on_delete=models.CASCADE)

class Student(Model):
    user_key = models.ForeignKey(User, on_delete=models.CASCADE)
    number = models.PositiveSmallIntegerField()
