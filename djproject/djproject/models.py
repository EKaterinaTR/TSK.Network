from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import F, Sum

User = get_user_model()

class VKUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    vk_key = models.CharField(max_length=100)

class StateGraph(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_build = models.BooleanField(default=False)