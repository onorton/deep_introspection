from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import base64
import json
import urllib.parse

@csrf_exempt
def index(request):
    if request.method == 'POST':
        body = json.loads(request.body.decode("utf-8"))
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

        # Do something smart with charset and b64 instead of assuming

        with open('images/'+body['name'], "wb") as f:
            f.write(base64.b64decode(data))
        return HttpResponse("{message: \"File successfully uploaded.\"}")
    return HttpResponse("{message: \"Invalid method.\"}")
