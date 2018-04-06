from django.db import models

class TestImage(models.Model):
    hash = models.CharField(max_length=255)
    image = models.ImageField(upload_to='images')
    user = models.IntegerField(default=0)
