from deep_introspection import features
from deep_introspection import lrp
from deep_introspection import utils

import numpy as np

from deep_introspection import lrp


import caffe

def test_captures_disctinct_features():

    caffe.set_device(0)  # if we have multiple GPUs, pick the first one
    caffe.set_mode_gpu()

    net = caffe.Classifier('deep_introspection/test/VGG.prototxt', 'deep_introspection/test/VGG_ILSVRC_16_layers.caffemodel', caffe.TEST,channel_swap=(2,1,0))

    img, offset, resFac, newSize = utils.imgPreprocess(img_path='deep_introspection/test/cat.jpg')
    net.image_dims = newSize
    relevances = lrp.calculate_lrp_heatmap(net, img)

    clusters = features.extract_features_from_relevances(relevances)

    # Checks that all clusters have more than 10 points
    assert(all(map(lambda x: len(x) > 10, clusters)))

    # Checks that all points are greater than the threshold
    for cluster in clusters:
        assert(all(map(lambda x: abs(relevances[x]) >= 5/relevances.flatten().shape[0], cluster)))
