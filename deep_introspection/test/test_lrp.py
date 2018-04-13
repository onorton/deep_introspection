from deep_introspection import lrp
from deep_introspection import utils, network

import matplotlib.pyplot as plt

import numpy as np
import caffe

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
    net = network.CaffeNet('deep_introspection/test/VGG.prototxt', 'deep_introspection/test/VGG_ILSVRC_16_layers.caffemodel')

    img, offset, resFac, newSize = utils.imgPreprocess(img_path='deep_introspection/test/cat.jpg')
    net.set_new_size(newSize)
    relevances = lrp.calculate_lrp_heatmap(net, img)

    assert(relevances.shape == (224,224))
