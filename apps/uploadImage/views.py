from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import base64
import json
import urllib.parse
import hashlib
from apps.uploadImage.models import TestImage

@csrf_exempt
def index(request):
    if request.method == 'POST':
        body = json.loads(request.body.decode("utf-8"))
        name = body['name']
        up = urllib.parse.urlparse(body['image'])
        head, data = up.path.split(',', 1)
        bits = head.split(';')
        mime_type = bits[0] if bits[0] else 'text/plain'
        charset, b64 = 'ASCII', False
        for bit in bits:
            if bit.startswith('charset='):
                charset = bit[8:]
            elif bit == 'base64':
                b64 = True

        # Hash the data to see if image already exists
        imgHash = hashlib.md5(data.encode('utf-8')).digest()
        if TestImage.objects.filter(hash=imgHash).count() == 0:
            img = TestImage(hash=imgHash, image='images/'+name)
            img.save()
            with open('images/'+name, "wb") as f:
                f.write(base64.b64decode(data))
            return HttpResponse("{\"id\":" + str(img.id) + ", \"filename\": \"" + name + "\", \"message\": \"File successfully uploaded.\"}")
        else:
            return HttpResponse("{}",status=409)
    elif request.method == 'GET':
        images = list(map(lambda item: {'id': item.id, 'url': item.image.url}, list(TestImage.objects.all())))
        return HttpResponse("{\"images\":"+ json.dumps(images) + "}")
    return HttpResponse("{message: \"Invalid method.\"}", status=405)
