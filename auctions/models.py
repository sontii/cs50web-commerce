from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import CASCADE


class User(AbstractUser):
    pass

class listings(models.Model):
    name = models.CharField(max_length=64, null=True)
    active = models.BooleanField(default=True)
    timest = models.DateTimeField(auto_now_add=True, blank=True)
    user = models.ForeignKey(User, on_delete=CASCADE, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    bid = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    itempic = models.ImageField(blank=True, null=True)
    category = models.CharField(max_length=64, blank=True, null=True)
    details = models.CharField(max_length=200, blank=True, null=True)
    winner = models.CharField(max_length=64, blank=True, null=True)

class bids(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE, null=True)
    bid = models.DecimalField(max_digits=6, decimal_places=2)
    item = models.ForeignKey(listings, on_delete=CASCADE, null=True)

class comments(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE, null=True)
    comment = models.CharField(max_length=255, blank=True)
    item = models.ForeignKey(listings, on_delete=CASCADE, null=True)
    
class wlist(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE, null=True)
    item = models.ForeignKey(listings, on_delete=CASCADE, null=True)
