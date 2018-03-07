from deep_introspection import features
from deep_introspection import lrp
from deep_introspection import utils

import matplotlib.pyplot as plt

import numpy as np

from deep_introspection import lrp


import caffe

def test_captures_disctinct_features():

    caffe.set_device(0)  # if we have multiple GPUs, pick the first one
    caffe.set_mode_gpu()

    plt.subplot(221)
    net = caffe.Classifier('deep_introspection/test/VGG.prototxt', 'deep_introspection/test/VGG_ILSVRC_16_layers.caffemodel', caffe.TEST,channel_swap=(2,1,0))

    img, offset, resFac, newSize = utils.imgPreprocess(img_path='deep_introspection/test/fox.jpg')
    net.image_dims = newSize
    relevances = lrp.calculate_lrp_heatmap(net, img,'deep_introspection/test/VGG.prototxt')

    plt.imshow(relevances)

    clusters = features.extract_features_from_relevances(relevances)

    for cluster in clusters:
        points = np.transpose(cluster)
        plt.scatter(points[1],points[0])

    plt.subplot(222)

    img, offset, resFac, newSize = utils.imgPreprocess(img_path='deep_introspection/test/cat.jpg')
    net.image_dims = newSize
    relevances = lrp.calculate_lrp_heatmap(net, img,'deep_introspection/test/VGG.prototxt')
    plt.imshow(relevances)

    clusters = features.extract_features_from_relevances(relevances)

    for cluster in clusters:
        points = np.transpose(cluster)
        plt.scatter(points[1],points[0])

    plt.subplot(223)

    img, offset, resFac, newSize = utils.imgPreprocess(img_path='deep_introspection/test/balloon.jpg')
    net.image_dims = newSize
    relevances = lrp.calculate_lrp_heatmap(net, img,'deep_introspection/test/VGG.prototxt')

    plt.imshow(relevances)

    clusters = features.extract_features_from_relevances(relevances)

    for cluster in clusters:
        points = np.transpose(cluster)
        plt.scatter(points[1],points[0])

    plt.subplot(224)

    img, offset, resFac, newSize = utils.imgPreprocess(img_path='deep_introspection/test/rooster.jpg')
    net.image_dims = newSize
    relevances = lrp.calculate_lrp_heatmap(net, img,'deep_introspection/test/VGG.prototxt')

    plt.imshow(relevances)

    clusters = features.extract_features_from_relevances(relevances)

    for cluster in clusters:
        points = np.transpose(cluster)
        plt.scatter(points[1],points[0])


    plt.show()
    assert(False)
