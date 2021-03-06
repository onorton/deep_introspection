from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from apps.evaluation.models import Feedback
from apps.uploadImage.models import TestImage
from apps.uploadModel.models import TestModel

import json

@csrf_exempt
def index(request, scope):
    id = request.user.id
    body = json.loads(request.body.decode("utf-8"))
    image = TestImage.objects.filter(id=body['image']).first()
    model = TestModel.objects.filter(id=body['model']).first()
    feedback = json.dumps(body['state'])
    feedback = Feedback(user=id, image=image, model=model, feedback=feedback, scope=scope)
    feedback.save()
    return HttpResponse("{}")
