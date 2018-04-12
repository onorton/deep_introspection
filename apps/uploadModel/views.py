from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import base64
import json
import urllib.parse
import glob
import os
import re
from apps.uploadModel.models import TestModel

def tryint(s):
    try:
        return int(s)
    except:
        return s

def alphanum_key(s):
    return [tryint(c) for c in re.split('([0-9]+)', s)]



@csrf_exempt
def index(request):
    if request.user.id ==  None:
        return HttpResponse("{}",status=401)
    id = request.user.id

    if request.method == 'GET':
        if TestModel.objects.filter(user=id).first() != None:
            models = TestModel.objects.filter(user=id)
            models = json.dumps(list(map(lambda model: {"name": model.name, "id" : model.id}, models)))
            return HttpResponse("{\"models\": " + models + ", \"message\": \"Model successfully retrieved.\"}")
        else:
            return HttpResponse("{\"models\": null, \"message\": \"No model exists.\"}", status=404)


    return HttpResponse("{\"message\": \"Invalid method.\"}", status=405)

@csrf_exempt
def weights(request):
    if request.user.id ==  None:
        return HttpResponse("{}",status=401)
    id = request.user.id

    if request.method == 'POST':
        body = json.loads(request.body.decode("utf-8"))
        name = body['name']
        filename =  str(id) + '_' + name + '_weights.caffemodel'
        if body['blobNum'] == -1:
            # Combine all parts of the file together
            files = glob.glob('models/'+filename+'.*')
            files.sort(key=alphanum_key)

            with open('models/'+filename, "ab") as mainFile:
                for partName in files:
                    with open(partName, "rb") as partFile:
                        mainFile.write(partFile.read())

            # Clean up parts
            for partName in files:
                os.remove(partName)

            # Add weights file to model
            model = TestModel.objects.filter(name=name, user=id).first()
            model.weights = 'models/'+filename
            model.save()
            return HttpResponse("{\"name\": \"" + name + "\", \"id\": " + str(model.id) + ",\"message\": \"Model successfully uploaded.\"}")
        save_file('models/'+filename+'.'+str(body['blobNum']), body['part'])
        return HttpResponse("{\"filename\": \"" + name + "\", \"message\": \"Part successfully uploaded.\"}")

@csrf_exempt
def tf_data(request):
    if request.user.id ==  None:
        return HttpResponse("{}",status=401)
    id = request.user.id

    if request.method == 'POST':
        body = json.loads(request.body.decode("utf-8"))
        name = body['name']
        directory =  str(id) + '_' + name
        filename = directory + '/' + body['filename']
        if body['blobNum'] == -1:
            # Combine all parts of the file together
            files = glob.glob('models/'+filename+'.*')
            files.sort(key=alphanum_key)

            with open('models/'+filename, "ab") as mainFile:
                for partName in files:
                    with open(partName, "rb") as partFile:
                        mainFile.write(partFile.read())

            # Clean up parts
            for partName in files:
                os.remove(partName)

            # Add weights file to model
            model = TestModel.objects.filter(name=name, user=id).first()
            model.weights = 'models/'+filename
            model.save()
            return HttpResponse("{\"name\": \"" + name + "\", \"id\": " + str(model.id) + ",\"message\": \"Model successfully uploaded.\"}")
        save_file('models/'+filename+'.'+str(body['blobNum']), body['part'])
        return HttpResponse("{\"filename\": \"" + name + "\", \"message\": \"Part successfully uploaded.\"}")

@csrf_exempt
def architecture(request):
    if request.user.id ==  None:
        return HttpResponse("{}",status=401)
    id = request.user.id

    if request.method == 'POST':
        body = json.loads(request.body.decode("utf-8"))
        name = body['name']
        filename = str(id) + '_' + name + '_architecture.prototxt'
        # Check if model already exists
        if TestModel.objects.filter(name=name, user=id).count() != 0:
            return HttpResponse("{}",status=409)

        save_file('models/'+filename, body['file'])
        model = TestModel(name=name, architecture='models/'+filename, user=id)
        model.save()
        return HttpResponse("{\"name\": \"" + name + "\", \"message\": \"Architecture successfully uploaded.\"}")
    return HttpResponse("{\"message\": \"Invalid method.\"}", status=405)

@csrf_exempt
def tf_architecture(request):
    if request.user.id ==  None:
        return HttpResponse("{}",status=401)
    id = request.user.id

    if request.method == 'POST':
        body = json.loads(request.body.decode("utf-8"))
        name = body['name']
        directory =  str(id) + '_' + name
        filename = directory + '/' + body['filename']
        if body['blobNum'] == -1:
            # Combine all parts of the file together
            files = glob.glob('models/'+filename+'.*')
            files.sort(key=alphanum_key)

            with open('models/'+filename, "ab") as mainFile:
                for partName in files:
                    with open(partName, "rb") as partFile:
                        mainFile.write(partFile.read())

            # Clean up parts
            for partName in files:
                os.remove(partName)

            model = TestModel.objects.filter(name=name, user=id).first()
            return HttpResponse("{\"name\": \"" + name + "\", \"id\": " + str(model.id) + ",\"message\": \"Model MetaGraph successfully uploaded.\"}")

        if body['blobNum'] == 0:
            # Check if model already exists
            if TestModel.objects.filter(name=name, user=id).count() != 0:
                return HttpResponse("{}",status=409)

            model = TestModel(name=name, architecture='models/'+filename, user=id)
            model.save()
            os.makedirs('models/'+directory)

        save_file('models/'+filename+'.'+str(body['blobNum']), body['part'])
        return HttpResponse("{\"filename\": \"" + name + "\", \"message\": \"Part successfully uploaded.\"}")



@csrf_exempt
def tf_index_checkpoint(request):
    if request.user.id ==  None:
        return HttpResponse("{}",status=401)
    id = request.user.id

    if request.method == 'POST':
        body = json.loads(request.body.decode("utf-8"))
        name = body['name']
        directory = str(id) + '_' + name

        index_name = directory +'/' + body['index_filename']
        checkpoint_name = directory + '/' + body['checkpoint_filename']

        model = TestModel.objects.filter(name=name, user=id).first()

        save_file('models/'+index_name, body['index_file'])
        model.index_file = 'models/'+index_name

        save_file('models/'+checkpoint_name, body['checkpoint'])
        model.checkpoint = 'models/'+checkpoint_name

        model.save()
        return HttpResponse("{\"name\": \"" + name + "\", \"message\": \"Index and checkpoint successfully uploaded.\"}")

@csrf_exempt
def tf_labels(request):
    if request.user.id ==  None:
        return HttpResponse("{}",status=401)
    id = request.user.id
    if request.method == 'POST':
        body = json.loads(request.body.decode("utf-8"))
        name = body['name']
        directory = str(id) + '_' + name
        filename = directory + '/' + body['filename']
        save_file('models/'+filename, body['file'])
        model = TestModel.objects.filter(name=name, user=id).first()
        model.labels = 'models/'+filename
        model.save()
        return HttpResponse("{\"name\": \"" + name + "\", \"message\": \"Labels successfully uploaded.\"}")
    return HttpResponse("{\"message\": \"Invalid method.\"}", status=405)

@csrf_exempt
def labels(request):
    if request.user.id ==  None:
        return HttpResponse("{}",status=401)
    id = request.user.id
    if request.method == 'POST':
        body = json.loads(request.body.decode("utf-8"))
        name = body['name']
        filename = str(id) + '_' + name +'_labels.txt'
        save_file('models/'+filename, body['file'])
        model = TestModel.objects.filter(name=name, user=id).first()
        model.labels = 'models/'+filename
        model.save()
        return HttpResponse("{\"name\": \"" + name + "\", \"message\": \"Labels successfully uploaded.\"}")
    return HttpResponse("{\"message\": \"Invalid method.\"}", status=405)

def save_file(path, file):
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
