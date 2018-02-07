from django.db import models

class TestExample(models.Model):
    name = models.CharField(max_length=255)
    originalImage = models.ImageField(upload_to='testImages')
