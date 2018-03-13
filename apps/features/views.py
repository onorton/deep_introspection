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

import os

import itertools

import matplotlib.pyplot as plt

from PIL import Image

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
        write_clusters(features_path, clusters)
        overlay_shape = (img.shape[0],img.shape[1],4)
        for i, cluster in enumerate(clusters):
            overlay_img = np.zeros(overlay_shape)
            for point in cluster:
                overlay_img[point[0],point[1],0] = 255
                overlay_img[point[0],point[1],3] = 128
            overlay_img = Image.fromarray(np.uint8(overlay_img))
            overlay_img.save('features/feature_model_'+ str(model) + '_image_' + str(image) +'_' + str(i) + '.png')

        write_clusters(features_path, clusters)
        feature_set = FeatureSet(model=test_model, image=TestImage.objects.filter(id=image).first(), features=features_path)
        feature_set.save()

    # Get number of features and return features
    with open(features_path) as f:
        num_features = sum(1 for _ in f)
        return HttpResponse("{\"features\":" + json.dumps(list(range(num_features))) + ", \"message\": \"Features successfully retrieved.\"}")

@csrf_exempt
def evaluate(request, model, image):
    features_path = 'features/model_'+ str(model) + '_image_' + str(image) + '.dat'
    body = json.loads(request.body.decode("utf-8"))
    inactive_indices = body['inactiveFeatures']
    clusters = read_clusters(features_path)
    inactive_features = list(itertools.chain.from_iterable([clusters[i] for i in inactive_indices]))
    inactive_features = list(itertools.chain.from_iterable(map(lambda x: [tuple(x+[0]),tuple(x+[1]),tuple(x+[2])], inactive_features)))
    img_path = TestImage.objects.filter(id=image).first().image
    test_model = TestModel.objects.filter(id=model).first()

    architecture = str(test_model.architecture)
    weights = str(test_model.weights)
    labels = str(test_model.labels)

    net = caffe.Classifier(architecture, weights, caffe.TEST,channel_swap=(2,1,0))

    img, offset, resFac, newSize = utils.imgPreprocess(img_path=img_path)
    net.image_dims = newSize

    random_nums = 256*np.random.uniform(size=img.shape)

    mean = np.array([103.939, 116.779, 123.68])

    for index in inactive_features:
        img[index] = random_nums[index]-mean[2-index[2]]

    net.predict([img],oversample=True)

    predictions = np.mean(net.blobs['prob'].data, axis=0)
    top_five = list(np.asarray(predictions.argsort()[-5:][::-1],  type('int', (int,), {})))
    predictions = np.asarray(predictions, type('float', (float,), {}))

    top_predictions = []
    if labels != None :
        labels = open(labels).readlines()
        top_predictions = list(map(lambda x: {'label':get_label(labels[x]), 'value': predictions[x]}, top_five))
    else :
        top_predictions = list(map(lambda x: {'label':x, 'value': predictions[x]}, top_five))


    img[:, :, 0] += mean[2]
    img[:, :, 1] += mean[1]
    img[:, :, 2] += mean[0]

    # save modified image
    img = Image.fromarray(np.uint8(img))
    modification_path = 'features/model_'+ str(model) + '_image_' + str(image) + '_' + '_'.join(str(f) for f in inactive_indices) + '.jpg'
    img.save(modification_path)

    return HttpResponse("{\"predictions\":" + json.dumps(top_predictions)+ ", \"image\": \""  + 'media/'+modification_path + "\"}")

def get_label(image_label):
    image_label = image_label.split(',')[0].strip()
    return image_label[image_label.index(' ')+1:]

def write_clusters(path, clusters):
    with open(path, "w") as f:
        for cluster in clusters:
            f.write(str(cluster)+'\n')

def read_clusters(path):
    clusters = []
    with open(path, "r") as f:
        content = f.readlines()
        for line in content:
            clusters.append(map(lambda x: list(x), eval(line.strip())))

    return clusters
