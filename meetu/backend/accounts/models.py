from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=20, unique=True)
    manner = models.FloatField(default=36.5)
    favorites = models.ManyToManyField('self', blank=True, symmetrical=False)

    def __str__(self):
        return self.nickname
