from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import os
import functools

from apps.features.models import FeatureSet
from apps.uploadModel.models import TestModel
from apps.uploadImage.models import TestImage

from scipy.misc import imread, imresize

from deep_introspection import lrp, utils, features, network

import caffe
import numpy as np

import json

import os

import itertools

import matplotlib.pyplot as plt

import math

import time

from PIL import Image

def get_top_predictions(predictions, num, labels):
        top_num = []
        if num != -1:
            top_num = list(np.asarray(predictions.argsort()[-5:][::-1],  type('int', (int,), {})))
        else:
            top_num = list(np.asarray(predictions.argsort()[::-1],  type('int', (int,), {})))

        predictions = np.asarray(predictions, type('float', (float,), {}))
        top_predictions = []
        if labels != None :
            labels = open(labels).readlines()
            top_predictions = list(map(lambda x: {'label':get_label(labels[x]), 'value': predictions[x], 'index': x}, top_num))
        else :
            top_predictions = list(map(lambda x: {'label':x, 'value': predictions[x], 'index': x}, top_num))
        return top_predictions

def predictions_from_features(net, img_path, inactive_features):


    if isinstance(net, network.TensorFlowNet):
        img = imread(img_path, mode='RGB')
        img = imresize(img, (224, 224))

        random_nums = 256*np.random.uniform(size=img.shape)

        for index in itertools.chain.from_iterable(inactive_features):
            img[index] = random_nums[index]

    else:
        img, offset, resFac, newSize = utils.imgPreprocess(img_path=img_path)
        net.set_new_size(newSize)

        random_nums = 256*np.random.uniform(size=img.shape)

        mean = np.array([103.939, 116.779, 123.68])


        for index in itertools.chain.from_iterable(inactive_features):
            img[index] = random_nums[index]-mean[2-index[2]]

    size = 4
    start = time.time()

    for cluster in inactive_features:
        if len(cluster) > 0:
            ymin = np.min(np.array(cluster)[:,0])
            ymax = np.max(np.array(cluster)[:,0])
            xmin = np.min(np.array(cluster)[:,1])
            xmax = np.max(np.array(cluster)[:,1])

            for i in range(ymin,ymax,size):
                for j in range(xmin,xmax,size):
                    for elem in cluster:
                        if elem[0] < i+size and elem[0] >= i and  elem[1] < j+size and elem[1] >= j:
                            img[i:i+size,j:j+size,0] = np.mean(img[i:i+size,j:j+size,0])
                            img[i:i+size,j:j+size,1] = np.mean(img[i:i+size,j:j+size,1])
                            img[i:i+size,j:j+size,2] = np.mean(img[i:i+size,j:j+size,2])
                            break


    predictions = net.predict(img)
    predictions = np.mean(predictions, axis=0)

    if isinstance(net, network.CaffeNet):
        img[:, :, 0] += mean[2]
        img[:, :, 1] += mean[1]
        img[:, :, 2] += mean[0]


    return predictions, img

def compare(item1, item2):
    if item1['difference'] < item2['difference']:
        return -1
    elif item1['difference'] > item2['difference']:
        return 1
    else:
        return 0

@csrf_exempt
def index(request, model, image):
    features_path = 'features/model_'+ str(model) + '_image_' + str(image) + '.dat'
    feature_set = FeatureSet.objects.filter(model__id=model,image__id=image).first()

    unmodified_path = 'features/model_'+ str(model) + '_image_' + str(image) + '_.jpg'

    if feature_set == None:
        # carry out LRP and clustering and write to file

        img_path = TestImage.objects.filter(id=image).first().image
        test_model = TestModel.objects.filter(id=model).first()

        architecture = str(test_model.architecture)
        weights = str(test_model.weights)
        labels = str(test_model.labels)

        if architecture.split(".")[-1].lower() == "meta":
            net = network.TensorFlowNet(architecture, './models/'+ str(test_model.user) +'_' + test_model.name + '/')
            img = imread(img_path, mode='RGB')
            img = imresize(img, (224, 224))
            im = Image.fromarray(np.uint8(img))
            im.save(unmodified_path)

        else:
            net = network.CaffeNet(architecture, weights)
            img = imread(img_path,mode='RGB')
            img = 256*utils.imageResize(img)
            img = Image.fromarray(np.uint8(img))
            img.save(unmodified_path)
            img, offset, resFac, newSize = utils.imgPreprocess(img_path=img_path)
            net.set_new_size(newSize)

        relevances = lrp.calculate_lrp_heatmap(net, img)
        clusters = features.extract_features_from_relevances(relevances)

        predictions, _ = predictions_from_features(net, img_path, [])
        basic_predictions = get_top_predictions(predictions, -1, labels)
        predicted = basic_predictions[0]

        sorted_predictions = []
        for i in range(len(clusters)):
            cluster = list(itertools.chain.from_iterable(map(lambda x: [x+(0,),x+(1,),x+(2,)], clusters[i])))
            predictions, _ = predictions_from_features(net, img_path, [cluster])
            diff = predicted['value'] - predictions[predicted['index']]
            sorted_predictions.append({'index':i,'difference':diff})


        sorted_predictions = sorted(sorted_predictions, key=functools.cmp_to_key(compare))
        sorted_predictions.reverse()

        clusters = list(map(lambda x: clusters[x['index']], sorted_predictions))

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
        return HttpResponse("{\"features\":" + json.dumps(list(range(num_features))) + ", \"image\": \""  + 'media/'+unmodified_path  + "\",\"message\": \"features successfully retrieved.\"}")

@csrf_exempt
def evaluate(request, model, image):
    features_path = 'features/model_'+ str(model) + '_image_' + str(image) + '.dat'

    body = json.loads(request.body.decode("utf-8"))
    inactive_indices = body['inactiveFeatures']
    clusters = read_clusters(features_path)
    inactive_features = [clusters[i] for i in inactive_indices]
    inactive_features = list(map(lambda cluster: list(itertools.chain.from_iterable(map(lambda x: [tuple(x+[0]),tuple(x+[1]),tuple(x+[2])], cluster))), inactive_features))

    img_path = TestImage.objects.filter(id=image).first().image
    test_model = TestModel.objects.filter(id=model).first()

    architecture = str(test_model.architecture)
    weights = str(test_model.weights)
    labels = str(test_model.labels)

    if architecture.split(".")[-1].lower() == "meta":
        net = network.TensorFlowNet(architecture, './models/'+ str(test_model.user) +'_' + test_model.name + '/')
    else:
        net = network.CaffeNet(architecture, weights)

    predictions, img = predictions_from_features(net, img_path, inactive_features)

    top_predictions = get_top_predictions(predictions, 5, labels)
    # save modified image
    img = Image.fromarray(np.uint8(img))
    modification_path = 'features/model_'+ str(model) + '_image_' + str(image) + '_' + '_'.join(str(f) for f in inactive_indices) + '.jpg'
    img.save(modification_path)
    return HttpResponse("{\"predictions\":" + json.dumps(top_predictions)+ ", \"image\": \""  + 'media/'+modification_path + "\"}")

@csrf_exempt
def analyse(request, model, image):

    features_path = 'features/model_'+ str(model) + '_image_' + str(image) + '.dat'
    clusters = read_clusters(features_path)
    num_clusters = len(clusters)

    img_path = TestImage.objects.filter(id=image).first().image
    test_model = TestModel.objects.filter(id=model).first()

    architecture = str(test_model.architecture)
    weights = str(test_model.weights)
    labels = str(test_model.labels)

    if architecture.split(".")[-1].lower() == "meta":
        net = network.TensorFlowNet(architecture, './models/'+ str(test_model.user) +'_' + test_model.name + '/')
    else:
        net = network.CaffeNet(architecture, weights)

    predictions, _ =  predictions_from_features(net, img_path, [])
    basic_predictions = get_top_predictions(predictions, -1, labels)
    predicted = basic_predictions[0]

    # Find features for largest change
    largest_change = 0
    features = []

    for i in range(1):
        num = np.random.randint(low=0,high=2**num_clusters)
        b = [num >> j & 1 for j in range(num.bit_length()-1,-1,-1)]
        b = [0] * (num_clusters-len(b)) + b
        inactive_indices = list(itertools.compress(range(num_clusters), b))
        inactive_features = [clusters[i] for i in inactive_indices]
        inactive_features = list(map(lambda cluster: list(itertools.chain.from_iterable(map(lambda x: [tuple(x+[0]),tuple(x+[1]),tuple(x+[2])], cluster))), inactive_features))


        predictions, img =  predictions_from_features(net, img_path, inactive_features)

        change = predicted['value'] - predictions[predicted['index']]
        if change > largest_change:
            largest_change = change
            features = inactive_indices

    inactive_features = [clusters[i] for i in features]
    inactive_features = list(map(lambda cluster: list(itertools.chain.from_iterable(map(lambda x: [tuple(x+[0]),tuple(x+[1]),tuple(x+[2])], cluster))), inactive_features))

    predictions, img =  predictions_from_features(net, img_path, inactive_features)

    img = Image.fromarray(np.uint8(img))
    modification_path = 'features/model_'+ str(model) + '_image_' + str(image) + '_' + '_'.join(str(f) for f in features) + '.jpg'
    img.save(modification_path)
    top_predictions = get_top_predictions(predictions, 5, labels)
    lc = {'features': features, 'predictions': top_predictions}

    # Find most important feature
    biggest_feature = 0
    biggest_change = 0
    for i in range(num_clusters):
        cluster = clusters[i]
        inactive_features = list(itertools.chain.from_iterable(map(lambda x: [tuple(x+[0]),tuple(x+[1]),tuple(x+[2])], cluster)))
        predictions, _ =  predictions_from_features(net, img_path, [inactive_features])
        change = predicted['value'] - predictions[predicted['index']]
        if change > biggest_change:
            biggest_change = change
            biggest_feature = i

    inactive_features = list(itertools.chain.from_iterable(map(lambda x: [tuple(x+[0]),tuple(x+[1]),tuple(x+[2])], clusters[biggest_feature])))
    predictions, img =  predictions_from_features(net, img_path, [inactive_features])
    img = Image.fromarray(np.uint8(img))
    modification_path = 'features/model_'+ str(model) + '_image_' + str(image) + '_' + str(biggest_feature) + '.jpg'
    img.save(modification_path)
    top_predictions = get_top_predictions(predictions, 5, labels)

    mi = {'feature': biggest_feature, 'predictions': top_predictions}

    # Find minimal features required
    selection = []
    features_found = False
    for num in range(num_clusters):
        if num == 0:
            inactive_features = list(itertools.chain.from_iterable(clusters))
            inactive_features = list(itertools.chain.from_iterable(map(lambda x: [tuple(x+[0]),tuple(x+[1]),tuple(x+[2])], inactive_features)))
            predictions, img =  predictions_from_features(net, img_path, [inactive_features])
            top_predictions = get_top_predictions(predictions, 5, labels)
            # No features are required
            if top_predictions[0]['index'] == predicted['index']:
                img = Image.fromarray(np.uint8(img))
                modification_path = 'features/model_'+ str(model) + '_image_' + str(image) + '_' + '_'.join(str(f) for f in range(num_clusters)) + '.jpg'
                img.save(modification_path)
                features_found = True
        else:
            combinations = itertools.combinations(range(num_clusters), num)
            for selection in combinations:
                inactive_indices = list(set(range(num_clusters)) - set(selection))
                inactive_features = [clusters[i] for i in inactive_indices]
                inactive_features = list(map(lambda cluster: list(itertools.chain.from_iterable(map(lambda x: [tuple(x+[0]),tuple(x+[1]),tuple(x+[2])], cluster))), inactive_features))


                predictions, img =  predictions_from_features(net, img_path, inactive_features)
                top_predictions = get_top_predictions(predictions, 5, labels)

                if top_predictions[0]['index'] == predicted['index']:
                    img = Image.fromarray(np.uint8(img))
                    modification_path = 'features/model_'+ str(model) + '_image_' + str(image) + '_' + '_'.join(str(f) for f in inactive_indices) + '.jpg'
                    img.save(modification_path)
                    features_found = True
                    break
        if features_found:
            break

    mfRequired = {'features': selection, 'predictions': top_predictions}

    # Find minimal to change
    selection = []
    features_found = False
    for num in range(num_clusters):
        if num == 0:
            continue

        combinations = itertools.combinations(range(num_clusters), num)
        for selection in combinations:
            inactive_indices = list(selection)
            inactive_features = [clusters[i] for i in inactive_indices]
            inactive_features = list(map(lambda cluster: list(itertools.chain.from_iterable(map(lambda x: [tuple(x+[0]),tuple(x+[1]),tuple(x+[2])], cluster))), inactive_features))


            predictions, img =  predictions_from_features(net, img_path, inactive_features)
            top_predictions = get_top_predictions(predictions, 5, labels)
            if top_predictions[0]['index'] != predicted['index']:
                img = Image.fromarray(np.uint8(img))
                modification_path = 'features/model_'+ str(model) + '_image_' + str(image) + '_' + '_'.join(str(f) for f in inactive_indices) + '.jpg'
                img.save(modification_path)
                features_found = True
                break

        if features_found:
            break

    if not features_found:
        selection = []
    mfPerturbation = {'features': selection, 'predictions': top_predictions}

    results = {'originalClass':predicted['label'],
            'lc': lc,
            'mi': mi,
            'mfRequired':mfRequired,
            'mfPerturbation':mfPerturbation}

    return HttpResponse("{\"results\":" + json.dumps(results) +"}")


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
            clusters.append(list(map(lambda x: list(x), eval(line.strip()))))

    return clusters
