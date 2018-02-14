import numpy as np

def get_layer_names(net) :
    """Calculates the layer-wise relevance propagations for a given im
    inputs
    img: Test image as numpy array
    net: caffe network
    output
    outgoing discriminative locations of current layer
    """

    layer_names = []

    for i in range(len(list(net._layer_names))):
        if net.layers[i].type == 'Convolution' or net.layers[i].type == 'Pooling' or net.layers[i].type == 'InnerProduct':
            layer_names.append(net._layer_names[i])

    return layer_names
