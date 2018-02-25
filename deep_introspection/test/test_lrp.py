from deep_introspection import lrp
from deep_introspection import utils

import matplotlib.pyplot as plt

import numpy as np
import caffe

def test_layers_found_should_be_in_order():
    caffe.set_device(0)  # if we have multiple GPUs, pick the first one
    caffe.set_mode_gpu()
    net = caffe.Net('deep_introspection/test/VGG.prototxt',caffe.TEST)
    layer_names = lrp.get_layer_names(net)
    assert(layer_names == ['data','conv1_1','conv1_2','pool1','conv2_1','conv2_2','pool2','conv3_1','conv3_2','conv3_3','pool3','conv4_1','conv4_2','conv4_3','pool4','conv5_1','conv5_2','conv5_3','pool5','fc6','fc7','fc8'])

def test_relevances_propagated_fully_connected_layers():
    # Example from a 2 neuron fully connected layer to a 2 neuron fully connected layer
    relevances = np.array([0.5, 0.4])
    weights = np.array([[0.2, -1],[0.3, -0.7]])
    activations = np.array([0.1, 0.4])
    assert(np.isclose(lrp.propagate_fully_connected(relevances, weights, activations, 0.5), np.array([0.08834586,0.36165414])).all())

def test_relevances_propagated_fully_connected_layers_different_sizes():
    # Example from a 3 neuron fully connected layer to a 2 neuron fully connected layer
    relevances = np.array([0.5, 0.4, 0.3])
    weights = np.array([[0.2, -1, 0.4],[0.3, -0.7, -0.2]])
    activations = np.array([0.1, 0.4])
    assert(np.isclose(lrp.propagate_fully_connected(relevances, weights, activations, 0.5), np.array([0.238345865,0.51165414])).all())


def test_lrp_image():
    caffe.set_device(0)  # if we have multiple GPUs, pick the first one
    caffe.set_mode_gpu()
    net = caffe.Classifier('deep_introspection/test/VGG.prototxt', 'deep_introspection/test/VGG_ILSVRC_16_layers.caffemodel', caffe.TEST,channel_swap=(2,1,0))

    img, offset, resFac, newSize = utils.imgPreprocess(img_path='deep_introspection/test/cat.jpg')
    net.image_dims = newSize
    relevances = lrp.calculate_lrp_heatmap(net, img,'deep_introspection/test/VGG.prototxt', 'deep_introspection/test/VGG_ILSVRC_16_layers.caffemodel')

    assert(relevances.shape == (224,224))
