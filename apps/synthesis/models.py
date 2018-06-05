from django.db import models

from apps.uploadModel.models import TestModel
from apps.uploadImage.models import TestImage

class FeatureImage(models.Model):
    model = models.ForeignKey(TestModel, default=None, on_delete=models.CASCADE)
    image = models.ForeignKey(TestImage, default=None, on_delete=models.CASCADE)
    feature = models.IntegerField()
    feature_image = models.ImageField(upload_to='synthesised_features')
