from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from deep_introspection import synthesis, network, utils

from apps.uploadModel.models import TestModel
from apps.uploadImage.models import TestImage
from apps.synthesis.models import FeatureImage
from apps.features.views import read_clusters

import json

import caffe
import numpy as np

import json

from PIL import Image

@csrf_exempt
def index (request, model, image, feature):
    if request.method == 'GET':
        images = list(map(lambda x: {'src': '/media/'+str(x.feature_image), 'thumbnail': '/media/'+str(x.feature_image)}, FeatureImage.objects.filter(model__id=model,image__id=image, feature=feature)))
        return HttpResponse("{\"images\": " + json.dumps(images) +"}")
    else:
        return HttpResponse("{message: \"Invalid method.\"}", status=405)


@csrf_exempt
def synthesise(request, model, image, feature):
    if request.method == 'POST':
        features_path = 'features/model_'+ str(model) + '_image_' + str(image) + '.dat'

        clusters = read_clusters(features_path)

        cluster = np.array(clusters[feature])


        img_path = TestImage.objects.filter(id=image).first().image
        test_model = TestModel.objects.filter(id=model).first()

        architecture = str(test_model.architecture)
        weights = str(test_model.weights)
        labels = str(test_model.labels)

        if architecture.split(".")[-1].lower() == "meta":
            net = network.TensorFlowNet(architecture, './models/'+ str(test_model.user) +'_' + test_model.name + '/')
            img = imread(img_path, mode='RGB')
            img = imresize(img, (224, 224))

        else:
            net = network.CaffeNet(architecture, weights)
            img, offset, resFac, newSize = utils.imgPreprocess(img_path=img_path)
            net.set_new_size(newSize)

        xmax, ymax, xmin, ymin = np.max(cluster[:,0]), np.max(cluster[:,1]), np.min(cluster[:,0]), np.min(cluster[:,1])

        feature_img, _ = synthesis.synthesise_boundary(net, img, xmax, ymax, xmin, ymin)
        mean = np.array([103.939, 116.779, 123.68])
        feature_img[:,:,0] += mean[2]
        feature_img[:,:,1] += mean[1]
        feature_img[:,:,2] += mean[0]

        num = FeatureImage.objects.filter(model__id=model,image__id=image,feature=feature).count()

        # save synthesised image
        feature_img = Image.fromarray(np.uint8(feature_img))
        feature_path = 'synthesised_features/model_'+ str(model) + '_image_' + str(image) + '_' + str(feature) + '_' + str(num) + '.jpg'
        feature_img.save(feature_path)

        featureImage = FeatureImage(model = test_model, image=TestImage.objects.filter(id=image).first(), feature=feature, feature_image=feature_path)
        featureImage.save()
        return HttpResponse("{\"image\": " + feature_path +"}")
    else:
        return HttpResponse("{message: \"Invalid method.\"}", status=405)
