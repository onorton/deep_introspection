from deep_introspection.lrp import calculate_lrp_heatmap
from deep_introspection.features import extract_features_from_relevances
from deep_introspection.fixations import fixations
from deep_introspection import network, utils

import matplotlib.pyplot as plt

import caffe

import numpy as np
import scipy as sp
import scipy.stats

import os
import time

import itertools

def mean_confidence_interval(data, confidence=0.95):
    a = 1.0*np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * sp.stats.t._ppf((1+confidence)/2., n-1)
    return m, h


def sa(net, img):
    net.predict(img)
    layer = 'prob'
    activations = net.get_activations(layer)

    grad = net.backward(layer, activations)
    return np.mean(np.abs(grad), axis=2)



net = network.CaffeNet('deep_introspection/test/VGG.prototxt', 'deep_introspection/test/VGG_ILSVRC_16_layers.caffemodel')
path = "deep_introspection\\test\\"
full_path = os.getcwd()+"\\" + path

test_files = []
for _, dirnames, filenames in os.walk(full_path):
    for file in filenames:
        if file.endswith('.jpg'):
            test_files.append(path+file)


#### Speed Evaluation ####
times = np.zeros((len(test_files), 4))
avg = 0

for i in range(len(test_files)):
    filename = test_files[i]
    img, offset, resFac, newSize = utils.imgPreprocess(img_path=filename)
    net.set_new_size(newSize)

    start = time.time()
    net.predict(img)
    avg += (time.time()-start)

    start = time.time()
    sa(net, img)
    times[i,0] = time.time()-start

    start = time.time()
    relevances = calculate_lrp_heatmap(net, img)
    times[i,2] = time.time()-start

    start = time.time()
    extract_features_from_relevances(relevances)
    times[i,3] = time.time()-start+times[i,2]

    start = time.time()
    points = fixations(net, img, offset, resFac)
    utils.obtain_heatmap(points, img)
    times[i,1] = (time.time()-start)/5

avg/=len(test_files)
# subtract prediction time
times -= avg

for i in range(times.shape[1]):
    print(mean_confidence_interval(times[:,i]))

########

#### Accuracy Evaluation ####

for i in range(len(test_files)):

    filename = test_files[1]

    img, offset, resFac, newSize = utils.imgPreprocess(img_path=filename)
    net.set_new_size(newSize)

    sa_result = sa(net, img)
    relevances = calculate_lrp_heatmap(net, img)
    points = fixations(net, img, offset, resFac)
    hm = utils.obtain_heatmap(points, img)[:224,:224]
    features = np.array(extract_features_from_relevances(np.copy(relevances)))
    features = list(itertools.chain.from_iterable(features))

    features_map = np.zeros(relevances.shape)
    for index in features:
        features_map[index] = relevances[index]


    mean = np.array([103.939, 116.779, 123.68])
    img[:, :, 0] += mean[2]
    img[:, :, 1] += mean[1]
    img[:, :, 2] += mean[0]
    img /= 255

    _, ax = plt.subplots(1, 4, figsize=(20, 5))
    ax[0].imshow(img), ax[0].axis('off'), ax[0].imshow(sa_result, 'jet', alpha=0.8), ax[0].set_title('Sensitivity Analysis')
    ax[1].imshow(img), ax[1].axis('off'), ax[1].imshow(relevances, 'jet', alpha=0.8,vmin=0, vmax=1e-3), ax[1].set_title('LRP')
    ax[2].imshow(img), ax[2].axis('off'), ax[2].imshow(hm, 'jet', alpha=0.8), ax[2].set_title('CNN Fixations')
    ax[3].imshow(img), ax[3].axis('off'), ax[3].imshow(features_map, 'jet', alpha=0.8, vmin=0, vmax=1e-3), ax[3].set_title('Our Method')

    plt.show()

########
