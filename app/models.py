from django.db import models

class Model(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Sex(Model):
    name = models.CharField(max_length=50)

class User(Model):
    name = models.CharField(max_length=20)
    email = models.CharField(max_length=50)
    sex = models.ForeignKey(Sex, on_delete=models.PROTECT)

class Teacher(Model):
    user = models.ForeignKey(Sex, on_delete=models.CASCADE)

class Student(Model):
    user = models.ForeignKey(Sex, on_delete=models.CASCADE)
    number = models.IntegerField(max_length=4)
