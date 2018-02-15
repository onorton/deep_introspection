from deep_introspection import lrp
import numpy as np
import caffe

def test_layers_found_should_be_in_order():
    caffe.set_device(0)  # if we have multiple GPUs, pick the first one
    caffe.set_mode_gpu()
    net = caffe.Net('deep_introspection/test/VGG.prototxt',caffe.TEST)
    layer_names = lrp.get_layer_names(net)
    assert(layer_names == ['conv1_1','conv1_2','pool1','conv2_1','conv2_2','pool2','conv3_1','conv3_2','conv3_3','pool3','conv4_1','conv4_2','conv4_3','pool4','conv5_1','conv5_2','conv5_3','pool5','fc6','fc7','fc8'])

def test_relevances_propagated_fully_connected_layers():
    # Example from a 2 neuron fully connected layer to a 2 neuron fully connected layer
    relevances = np.array([0.5, 0.4])
    weights = np.array([[0.2, -1],[0.3, -0.7]])
    activations = np.array([0.1, 0.4])
    assert(np.isclose(lrp.propagate_fully_connected(relevances, weights, activations, 0.5), np.array([0.08834586,0.36165414])).all())
