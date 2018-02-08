from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import base64
import json
import urllib.parse
import glob
import os
from uploadModel.models import TestModel

@csrf_exempt
def index(request):
    if request.method == 'POST':
        body = json.loads(request.body.decode("utf-8"))
        name = body['name']
        filename = body['filename']
        if body['blobNum'] == -1:
            # Combine all parts of the file together
            files = glob.glob('models/'+filename+'.*')
            with open('models/'+filename, "ab") as mainFile:
                for partName in files:
                    with open(partName, "rb") as partFile:
                        mainFile.write(partFile.read())
            # Clean up parts
            for partName in files:
                os.remove(partName)
            # Add weights file to model
            model = TestModel.objects.filter(name=name).first()
            model.weights = 'models/'+filename
            model.save()
            return HttpResponse("{\"name\": \"" + name + "\", \"message\": \"Model successfully uploaded.\"}")
        saveFile('models/'+filename+'.'+str(body['blobNum']), body['part'])
        return HttpResponse("{\"filename\": \"" + name + "\", \"message\": \"Part successfully uploaded.\"}")
    return HttpResponse("{\"message\": \"Invalid method.\"}", status=405)

@csrf_exempt
def architecture(request):
    if request.method == 'POST':
        body = json.loads(request.body.decode("utf-8"))
        filename = body['filename']
        name = body['name']
        # Check if model already exists
        if TestModel.objects.filter(name=name).count() != 0:
            return HttpResponse("{}",status=409)

        saveFile('models/'+filename, body['file'])
        model = TestModel(name=name, architecture='models/'+filename)
        model.save()
        return HttpResponse("{\"name\": \"" + name + "\", \"message\": \"Architecture successfully uploaded.\"}")
    return HttpResponse("{\"message\": \"Invalid method.\"}", status=405)

@csrf_exempt
def labels(request):
    if request.method == 'POST':
        body = json.loads(request.body.decode("utf-8"))
        filename = body['filename']
        name = body['name']
        saveFile('models/'+filename, body['file'])
        model = TestModel.objects.filter(name=name).first()
        model.labels = 'models/'+filename
        model.save()
        return HttpResponse("{\"name\": \"" + name + "\", \"message\": \"Labels successfully uploaded.\"}")
    return HttpResponse("{\"message\": \"Invalid method.\"}", status=405)

def saveFile(path, file):
    up = urllib.parse.urlparse(file)
    head, data = up.path.split(',', 1)
    bits = head.split(';')
    mime_type = bits[0] if bits[0] else 'text/plain'
    charset, b64 = 'ASCII', False
    for bit in bits:
        if bit.startswith('charset='):
            charset = bit[8:]
        elif bit == 'base64':
            b64 = True
    with open(path, "wb") as f:
        f.write(base64.b64decode(data))
