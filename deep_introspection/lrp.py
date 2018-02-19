import numpy as np

def get_layer_names(net) :
    """Gets the layer names of relevant networks in order
    net: caffe network
    output
    list of layer names
    """

    layer_names = []

    for i in range(len(list(net._layer_names))):
        if net.layers[i].type == 'Convolution' or net.layers[i].type == 'Pooling' or net.layers[i].type == 'InnerProduct':
            layer_names.append(net._layer_names[i])

    return layer_names


def propagate_fully_connected(relevances, weights, activations, alpha):
    """Calculates the layer-wise relevance propagations for a given fully-connected layer
    inputs
    relevances: relevances of higher layer
    weights: weights from higher layer to current
    activations: activations for current layer
    alpha: value of weighting positive and negative weights
    output
    relevances of current layer
    """


    beta = alpha - 1
    number_current_neurons = weights.shape[0]
    number_higher_neurons = weights.shape[1]

    keep_positives = np.vectorize(lambda x : x if x >= 0 else 0, otypes=[float])
    keep_negatives = np.vectorize(lambda x : x if x < 0 else 0, otypes=[float])

    z_positive = np.matmul(keep_positives(np.transpose(weights)),activations)
    s_positive = relevances/(z_positive+0.00000000001)

    c_positive = np.matmul(keep_positives(weights),s_positive)

    z_negative = np.matmul(keep_negatives(np.transpose(weights)),activations)
    s_negative = relevances/(z_negative+0.00000000001)
    c_negative = np.matmul(keep_negatives(weights),s_negative)

    relevances_current = activations*(alpha*c_positive - beta*c_negative)

    return relevances_current

def propagate_pooling(relevances, activations, k, s):
    """Calculates the layer-wise relevance propagations for a given pooling layer
    inputs
    relevances: relevances of higher layer
    activations: activations for current layer
    output
    relevances of current layer
    """
    number_current_neurons = activations.shape[0]
    number_higher_neurons = relevances.shape[0]
    relevances_current = np.zeros(number_current_neurons)

    sum_activations = np.sum(activations)
    activations_stack = np.zeros(shape=(activations.shape[0],relevances.shape[0]))
    for i in range(relevances.shape[0]):
        activations_stack[:,i] = activations
    relevances_current = np.matmul(activations_stack, relevances)

    relevances_current /= sum_activations
    
    return relevances_current

def calculate_lrp_heatmap(net, img):
    """Calculates the layer-wise relevance propagations for a given network and image
    inputs
    net: relevances of higher layer
    activations: activations for current layer
    output
    relevances of current layer
    """
    layer_names = get_layer_names(net)
    net.predict([img])
    prediction = np.argmax(net.blobs['prob'].data[0])
    relevances = np.zeros(net.blobs['prob'].data.shape[1])
    relevances[prediction] = 1.0

    relevances = propagate_fully_connected(relevances, np.transpose(net.params['fc8'][0].data), net.blobs['fc7'].data[0], 2) # relevances of fc7
    relevances = propagate_fully_connected(relevances, np.transpose(net.params['fc7'][0].data), net.blobs['fc6'].data[0], 2) # relevances of fc6
    relevances = propagate_fully_connected(relevances, np.transpose(net.params['fc6'][0].data), net.blobs['pool5'].data[0].flatten(), 2) # relevances of pool5
    relevances = propagate_pooling(relevances, net.blobs['pool5'].data[0].flatten(), 2, 2) # relevances of pool5

    print(relevances)
