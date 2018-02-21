import numpy as np
import copy
import caffe
import time

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

def propagate_fully_to_conv(relevances, weights, activations, alpha):
    out_shape = activations.shape
    relevances = propagate_fully_connected(relevances, weights, activations.flatten(), alpha)
    return relevances.reshape(out_shape)


def propagate_conv(posNet, negNet, relevances, activations, weightsLayer,activationLayer, alpha):

    beta = alpha - 1

    positiveWeights = np.maximum(posNet.params[weightsLayer][0].data[...], 0)
    negativeWeights = np.minimum(negNet.params[weightsLayer][0].data[...], 0)

    posNet.params[weightsLayer][0].data[...] = positiveWeights
    posNet.params[weightsLayer][1].data[...] = 0
    negNet.params[weightsLayer][0].data[...] = negativeWeights
    negNet.params[weightsLayer][1].data[...] = 0

    posNet.blobs[activationLayer] = activations
    posNet.forward(start = activationLayer,end=weightsLayer)
    z = posNet.blobs[weightsLayer].data
    s = relevances/z
    posNet.blobs[weightsLayer] = s
    posNet.backward(start = weightsLayer, end = activationLayer)
    positive = posNet.blobs[activationLayer].data

    # negNet.blobs[activationLayer] = activations
    # negNet.forward(start = activationLayer,end=weightsLayer)
    # z = negNet.blobs[weightsLayer].data
    # s = relevances/z
    # negNet.blobs[weightsLayer] = s
    # negNet.backward(start = weightsLayer, end=activationLayer)
    # negative = negNet.blobs[activationLayer].data

    return activations*alpha*positive
    #(alpha*positive - beta*negative)

def propagate_pooling(net, relevances, activations, layer, k):
    """Calculates the layer-wise relevance propagations for a given pooling layer
    inputs
    relevances: relevances of higher layer
    activations: activations for current layer
    output
    relevances of current layer
    """

    net.blobs[layer] = activations
    net.forward(start = layer, end = layer)
    z = net.blobs[layer]
    s = relevances/z

    net.blobs[layer] = s
    net.backward(start = layer, end = layer)
    c = net.blobs[layer]
    assert(not np.isclose(z, c).all())

    relevances = z*c
    # Resize relevances when unpooling (Each neuron of k*k field has equal relevance)
    relevances_unpooled = np.zeros(shape=(relevances.flatten().shape[0],k*k))
    for i in range(k*k):
        relevances_unpooled[:,i] = relevances.flatten()
    relevances = relevances_unpooled.flatten().reshape((relevances.shape[0],relevances.shape[1]*k,relevances.shape[2]*k))
    return relevances

def calculate_lrp_heatmap(net, img, architecture, weights):
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
    relevances = propagate_fully_to_conv(relevances, np.transpose(net.params['fc6'][0].data), net.blobs['pool5'].data[0], 2) # relevances of pool5
    relevances = propagate_pooling(net, relevances, net.blobs['pool5'].data[0], 'pool5', 2) # relevances of conv5_3

    relevances = propagate_conv(generateNetCopy(architecture,weights), generateNetCopy(architecture, weights), relevances,  net.blobs['conv5_2'].data[0], 'conv5_3', 'conv5_2', 2) # relevances of conv5_2
    relevances = propagate_conv(generateNetCopy(architecture,weights), generateNetCopy(architecture, weights), relevances,  net.blobs['conv5_1'].data[0], 'conv5_2', 'conv5_1', 2)
    relevances = propagate_conv(generateNetCopy(architecture,weights), generateNetCopy(architecture, weights), relevances,  net.blobs['pool4'].data[0], 'conv5_1', 'pool4', 2)
    relevances = propagate_pooling(net, relevances, net.blobs['pool4'].data[0], 'pool4', 2) # relevances of conv4_3

    relevances = propagate_conv(generateNetCopy(architecture,weights), generateNetCopy(architecture, weights), relevances,  net.blobs['conv4_2'].data[0], 'conv4_3', 'conv4_2', 2)
    relevances = propagate_conv(generateNetCopy(architecture,weights), generateNetCopy(architecture, weights), relevances,  net.blobs['conv4_1'].data[0], 'conv4_2', 'conv4_1', 2)
    relevances = propagate_conv(generateNetCopy(architecture,weights), generateNetCopy(architecture, weights), relevances,  net.blobs['pool3'].data[0], 'conv4_1', 'pool3', 2)
    relevances = propagate_pooling(net, relevances, net.blobs['pool3'].data[0], 'pool3', 2) # relevances of conv3_3

    relevances = propagate_conv(generateNetCopy(architecture,weights), generateNetCopy(architecture, weights), relevances,  net.blobs['conv3_2'].data[0], 'conv3_3', 'conv3_2', 2)
    relevances = propagate_conv(generateNetCopy(architecture,weights), generateNetCopy(architecture, weights), relevances,  net.blobs['conv3_1'].data[0], 'conv3_2', 'conv3_1', 2)
    relevances = propagate_conv(generateNetCopy(architecture,weights), generateNetCopy(architecture, weights), relevances,  net.blobs['pool2'].data[0], 'conv3_1', 'pool2', 2)
    relevances = propagate_pooling(net, relevances, net.blobs['pool2'].data[0], 'pool2', 2) # relevances of conv2_2

    relevances = propagate_conv(generateNetCopy(architecture,weights), generateNetCopy(architecture, weights), relevances,  net.blobs['conv2_2'].data[0], 'conv2_2', 'conv2_1', 2)
    relevances = propagate_conv(generateNetCopy(architecture,weights), generateNetCopy(architecture, weights), relevances,  net.blobs['pool1'].data[0], 'conv2_1', 'pool1', 2)
    relevances = propagate_pooling(net, relevances, net.blobs['pool1'].data[0], 'pool1', 2) # relevances of conv1_2

    relevances = propagate_conv(generateNetCopy(architecture,weights), generateNetCopy(architecture, weights), relevances,  net.blobs['conv1_1'].data[0], 'conv1_2', 'conv1_1', 2)
	# Finally do input layer

    print("Final relevances: " + str(relevances.shape))

def generateNetCopy(architecture, weights):
    return caffe.Classifier(architecture, weights, caffe.TEST,channel_swap=(2,1,0))
