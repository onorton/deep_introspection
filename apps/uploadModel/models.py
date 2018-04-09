from django.db import models

class TestModel(models.Model):
    name = models.CharField(max_length=255)
    architecture = models.FileField(upload_to='models')
    weights = models.FileField(upload_to='models')
    index_file = models.FileField(upload_to='models', null=True)
    checkpoint = models.FileField(upload_to='models', null=True)

    labels = models.FileField(upload_to='models', null=True)
    user = models.IntegerField(default=0)
