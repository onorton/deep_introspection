from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import base64
import json
import urllib.parse
import glob
import os

@csrf_exempt
def index(request):
    if request.method == 'POST':
        body = json.loads(request.body.decode("utf-8"))
        name = body['name']
        if body['blobNum'] == -1:
            # Combine all parts of the file together
            files = glob.glob('models/'+name+'.*')
            with open('models/'+name, "ab") as mainFile:
                for partName in files:
                    with open(partName, "rb") as partFile:
                        mainFile.write(partFile.read())
            # Clean up parts
            for partName in files:
                os.remove(partName)
            return HttpResponse("{\"filename\": \"" + name + "\", \"message\": \"Model successfully uploaded.\"}")

        up = urllib.parse.urlparse(body['part'])
        head, data = up.path.split(',', 1)
        bits = head.split(';')
        mime_type = bits[0] if bits[0] else 'text/plain'
        charset, b64 = 'ASCII', False
        for bit in bits:
            if bit.startswith('charset='):
                charset = bit[8:]
            elif bit == 'base64':
                b64 = True
        with open('models/'+ name + '.' + str(body['blobNum']), "wb") as f:
            f.write(base64.b64decode(data))
        return HttpResponse("{\"filename\": \"" + name + "\", \"message\": \"Part successfully uploaded.\"}")
    return HttpResponse("{\"message\": \"Invalid method.\"}", status=405)

@csrf_exempt
def architecture(request):
    if request.method == 'POST':
        body = json.loads(request.body.decode("utf-8"))
        name = body['name']

        up = urllib.parse.urlparse(body['file'])
        head, data = up.path.split(',', 1)
        bits = head.split(';')
        mime_type = bits[0] if bits[0] else 'text/plain'
        charset, b64 = 'ASCII', False
        for bit in bits:
            if bit.startswith('charset='):
                charset = bit[8:]
            elif bit == 'base64':
                b64 = True
        with open('models/'+ name, "wb") as f:
            f.write(base64.b64decode(data))
        return HttpResponse("{\"filename\": \"" + name + "\", \"message\": \"architecture successfully uploaded.\"}")
    return HttpResponse("{\"message\": \"Invalid method.\"}", status=405)
