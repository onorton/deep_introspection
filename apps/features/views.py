from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from apps.features.models import FeatureSet
from apps.uploadModel.models import TestModel
from apps.uploadImage.models import TestImage

from deep_introspection import lrp
from deep_introspection import utils
from deep_introspection import features

import caffe
import numpy as np

import json

@csrf_exempt
def index(request, model, image):
    features_path = 'features/model_'+ str(model) + '_image_' + str(image) + '.dat'
    feature_set = FeatureSet.objects.filter(model__id=model,image__id=image).first()
    if feature_set == None:
        # carry out LRP and clustering and write to file

        img_path = TestImage.objects.filter(id=image).first().image
        test_model = TestModel.objects.filter(id=model).first()

        architecture = str(test_model.architecture)
        weights = str(test_model.weights)

        net = caffe.Classifier(architecture, weights, caffe.TEST,channel_swap=(2,1,0))

        img, offset, resFac, newSize = utils.imgPreprocess(img_path=img_path)
        net.image_dims = newSize
        relevances = lrp.calculate_lrp_heatmap(net, img, architecture)
        clusters = features.extract_features_from_relevances(relevances)

        write_clusters(features_path,clusters)
        feature_set = FeatureSet(model=test_model, image=TestImage.objects.filter(id=image).first(), features=features_path)
        feature_set.save()

    # Get number of features and return features
    with open(features_path) as f:
        num_features = sum(1 for _ in f)
        return HttpResponse("{\"features\":" + json.dumps(list(range(num_features))) + ", \"message\": \"Features successfully retrieved.\"}")

def write_clusters(path, clusters):
    with open(path, "w") as f:
        for cluster in clusters:
            f.write(str(cluster)+'\n')
