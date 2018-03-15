from django.db import models

from apps.uploadImage.models import TestImage
from apps.uploadModel.models import TestModel

class FeatureSet(models.Model):
    model = models.ForeignKey(TestModel, default=None, on_delete=models.CASCADE)
    image = models.ForeignKey(TestImage, default=None, on_delete=models.CASCADE)
    features = models.FileField(upload_to='features')
