from django.db import models

class UserData(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    provider = models.CharField(max_length=50, null=True, blank=True)  # 'google', 'facebook', 'apple' etc.

    def __str__(self):
        return self.email
