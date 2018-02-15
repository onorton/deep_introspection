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
    relevances_current = np.zeros(number_current_neurons)

    for j in range(number_current_neurons):
        for k in range(number_higher_neurons):
            if weights[j,k] >= 0:
                # calculate positive component
                positive = weights[j,k]*activations[j]
                keep_positives = np.vectorize(lambda x : x if x >= 0 else 0, otypes=[float])
                sum_mults = np.matmul(keep_positives(weights[:,k]),np.transpose(activations))
                positive /= sum_mults
                relevances_current[j] += relevances[k]*alpha*positive
            else:
                negative = weights[j,k]*activations[j]
                keep_negatives = np.vectorize(lambda x : x if x < 0 else 0, otypes=[float])
                sum_mults = np.matmul(keep_negatives(weights[:,k]),np.transpose(activations))
                negative/= sum_mults
                relevances_current[j] -= relevances[k]*beta*negative
    print(relevances_current)
    return relevances_current
