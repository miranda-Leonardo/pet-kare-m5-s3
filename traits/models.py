from django.db import models

# Create your models here.
class Trait(models.Model):
    trait_name = models.CharField(max_length=20, unique=True)
    created_at = models.DateField(auto_now_add=True)
