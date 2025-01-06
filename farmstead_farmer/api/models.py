from django.contrib.auth.models import AbstractUser
from django.db import models

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    firstname = models.CharField(max_length=100, blank=False)
    lastname = models.CharField(max_length=100, blank=False)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True)
    favorites = models.JSONField(default=list, blank=True)
    last_activity = models.DateTimeField(default=now)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_username_update = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username
    
    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url.replace('/media/', '')
        return None

class OTP(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OTP {self.code} for {self.email}"