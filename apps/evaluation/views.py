from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from apps.evaluation.models import Feedback
from apps.uploadImage.models import TestImage
from apps.uploadModel.models import TestModel

import json

@csrf_exempt
def index(request):
    id = request.user.id
    body = json.loads(request.body.decode("utf-8"))
    image = TestImage.objects.filter(id=body['image']).first()
    model = TestModel.objects.filter(id=body['model']).first()
    feedback = Feedback(user=id, image=image, model=model, general_feedback=body['general'])
    feedback.save()
    return HttpResponse("{}")
