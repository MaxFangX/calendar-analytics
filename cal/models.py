from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):

    user = models.OneToOneField(User)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class GCalendar(models.Model):

    user = models.ForeignKey(User)
