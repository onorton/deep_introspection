from django.db import models

from apps.uploadImage.models import TestImage
from apps.uploadModel.models import TestModel

class Feedback(models.Model):
    model = models.ForeignKey(TestModel, default=None, on_delete=models.CASCADE)
    image = models.ForeignKey(TestImage, default=None, on_delete=models.CASCADE)
    user = models.IntegerField(default=0)
    feedback = models.TextField()
    time_submitted = models.DateTimeField(auto_now_add=True)
