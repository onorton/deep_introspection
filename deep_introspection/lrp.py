import numpy as np
import copy
import caffe
import time
from deep_introspection import im2col

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


def propagate_conv(net, relevances, activations, weightsLayer,activationLayer, alpha):
    beta = alpha - 1

    positiveWeights = np.maximum(net.params[weightsLayer][0].data[...], 1e-9)
    negativeWeights = np.minimum(net.params[weightsLayer][0].data[...], -1e-9)

    z = forward(activations, positiveWeights, net.blobs[weightsLayer].data[0].shape)
    s = alpha*relevances/z
    positive = backprop(s, positiveWeights, activations)

    z = forward(activations, negativeWeights, net.blobs[weightsLayer].data[0].shape)
    s = beta*relevances/z
    negative = backprop(s, negativeWeights, activations)

    return activations*(positive - negative)

def propagate_first_conv(net, relevances, activations, weightsLayer, activationLayer, h, l):
    positiveWeights = np.maximum(net.params[weightsLayer][0].data[...], 0)
    negativeWeights = np.minimum(net.params[weightsLayer][0].data[...], 0)
    weights = net.params[weightsLayer][0].data[...]

    X,L,H = activations,0*activations+l,0*activations+h

    z = forward(X, weights, net.blobs[weightsLayer].data[0].shape) - forward(L, positiveWeights, net.blobs[weightsLayer].data[0].shape) - forward(H, negativeWeights, net.blobs[weightsLayer].data[0].shape)+1e-9
    s = relevances/z

    return X*backprop(s, weights, X) - L*backprop(s, positiveWeights, L) - H*backprop(s, negativeWeights, H)

def forward(x, w, shape):
    if len(x.shape) == 3:
        x = x.reshape((1,)+x.shape)
    x_col = im2col.im2col_indices(x, 3, 3)
    w_col = w.reshape(w.shape[0],w.shape[1]*w.shape[2]*w.shape[3])

    out = np.matmul(w_col,x_col)
    out = out.reshape((shape[0], shape[1], shape[2], 1))
    out = out.transpose(3, 0, 1, 2)
    return out

def backprop(s, weights, x):
    s_reshaped = s
    if len(s.shape) == 3:
        s_reshaped = np.zeros(shape=(1, s.shape[0],s.shape[1],s.shape[2]))
        s_reshaped[0] = s
    s_reshaped = np.transpose(s_reshaped, (1,2,3,0))
    s_reshaped = s_reshaped.reshape((s_reshaped.shape[0],s_reshaped.shape[1]*s_reshaped.shape[2]*s_reshaped.shape[3]))

    x = x.reshape(tuple([1]+list(x.shape)))

    x_col = im2col.im2col_indices(x, 3, 3)

    dW = np.matmul(s_reshaped, np.transpose(x_col))
    dW = dW.reshape(weights.shape)
    W_reshape = weights.reshape((weights.shape[0],weights.shape[1]*weights.shape[2]*weights.shape[3]))
    dX_col = np.matmul(np.transpose(W_reshape), s_reshaped)
    dX = im2col.col2im_indices(dX_col, x.shape, 3, 3)
    return dX[0]

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
    print(layer)
    print(net.blobs[layer])
    print(activations)
    z = net.blobs[layer]+1e-9
    s = relevances/z

    net.blobs[layer] = s
    net.backward(start = layer, end = layer)
    c = net.blobs[layer]

    relevances = activations*c
    # Resize relevances when unpooling (Each neuron of k*k field has equal relevance)
    relevances_unpooled = np.zeros(shape=(relevances.flatten().shape[0],k*k))
    for i in range(k*k):
        relevances_unpooled[:,i] = relevances.flatten()/(k*k)
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
    relevances = np.zeros(net.blobs['prob'].data[0].shape)
    relevances[prediction] = 1.0
    l = np.amin(img)
    h = np.amax(img)

    relevances = propagate_fully_connected(relevances, np.transpose(net.params['fc8'][0].data), net.blobs['fc7'].data[0], 1) # relevances of fc7
    relevances = propagate_fully_connected(relevances, np.transpose(net.params['fc7'][0].data), net.blobs['fc6'].data[0], 1) # relevances of fc6
    relevances = propagate_fully_to_conv(relevances, np.transpose(net.params['fc6'][0].data), net.blobs['pool5'].data[0], 1) # relevances of pool5
    relevances = propagate_pooling(net, relevances, net.blobs['pool5'].data[0], 'pool5', 2) # relevances of conv5_3

    relevances = propagate_conv(net, relevances,  net.blobs['conv5_2'].data[0], 'conv5_3', 'conv5_2', 1) # relevances of conv5_2
    relevances = propagate_conv(net, relevances,  net.blobs['conv5_1'].data[0], 'conv5_2', 'conv5_1', 1)
    relevances = propagate_conv(net, relevances,  net.blobs['pool4'].data[0], 'conv5_1', 'pool4', 1)
    relevances = propagate_pooling(net, relevances, net.blobs['pool4'].data[0], 'pool4', 2) # relevances of conv4_3

    relevances = propagate_conv(net, relevances,  net.blobs['conv4_2'].data[0], 'conv4_3', 'conv4_2', 1)
    relevances = propagate_conv(net, relevances,  net.blobs['conv4_1'].data[0], 'conv4_2', 'conv4_1', 1)
    relevances = propagate_conv(net, relevances,  net.blobs['pool3'].data[0], 'conv4_1', 'pool3', 1)
    relevances = propagate_pooling(net, relevances, net.blobs['pool3'].data[0], 'pool3', 2) # relevances of conv3_3

    relevances = propagate_conv(net, relevances,  net.blobs['conv3_2'].data[0], 'conv3_3', 'conv3_2', 1)
    relevances = propagate_conv(net, relevances,  net.blobs['conv3_1'].data[0], 'conv3_2', 'conv3_1', 1)
    relevances = propagate_conv(net, relevances,  net.blobs['pool2'].data[0], 'conv3_1', 'pool2', 1)
    relevances = propagate_pooling(net, relevances, net.blobs['pool2'].data[0], 'pool2', 2) # relevances of conv2_2

    relevances = propagate_conv(net, relevances,  net.blobs['conv2_2'].data[0], 'conv2_2', 'conv2_1', 1)
    relevances = propagate_conv(net, relevances,  net.blobs['pool1'].data[0], 'conv2_1', 'pool1', 1)
    relevances = propagate_pooling(net, relevances, net.blobs['pool1'].data[0], 'pool1', 2) # relevances of conv1_2

    relevances = propagate_conv(net, relevances,  net.blobs['conv1_1'].data[0], 'conv1_2', 'conv1_1', 1)
	# Finally do input layer
    relevances = propagate_first_conv(net, relevances, net.blobs['data'].data[0], 'conv1_1', 'data', h, l)

    relevances =  np.mean(relevances.transpose(1,2,0), 2)

    return relevances

def generateNetCopy(architecture, weights):
    return caffe.Classifier(architecture, weights, caffe.TEST,channel_swap=(2,1,0))
