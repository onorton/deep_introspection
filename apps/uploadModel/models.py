from django.db import models

class TestModel(models.Model):
    name = models.CharField(max_length=255)
    architecture = models.FileField(upload_to='models')
    weights = models.FileField(upload_to='models')
    labels = models.FileField(upload_to='models')
    user = models.IntegerField(default=0)
