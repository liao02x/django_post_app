from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext as _
from .managers import UserManager
import logging


class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)

    objects = UserManager()

    signup_ip = models.GenericIPAddressField(null=True, blank=True)
    signup_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    signup_lon = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    signup_country = models.CharField(max_length=32, null=True, blank=True)
    signup_timezone = models.FloatField(null=True, blank=True)
    signup_holiday_info = models.JSONField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email



class Post(models.Model):
    title = models.CharField(max_length=100, blank=False, null=False, default=None, db_index=True)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    liked_by = models.ManyToManyField(to=User, blank=True, related_name='liked_posts')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Post"
        verbose_name_plural = "Posts"
