from django.db import models
from django.shortcuts import reverse
from django.contrib.auth import get_user_model

# Create your models here.
class Attack(models.Model):
    phone = models.CharField(max_length=12, verbose_name="Номер телефона")
    minute = models.IntegerField()
    description = models.TextField()
    active = models.BooleanField(default="1", verbose_name="Включен ли спам?")
    date = models.DateField(auto_now=True)




