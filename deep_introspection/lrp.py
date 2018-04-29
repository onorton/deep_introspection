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

    layer_names = ['data']

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

    positiveWeights = np.maximum(weights, 0)
    negativeWeights = np.minimum(weights, 0)

    z = np.matmul(np.transpose(positiveWeights),activations)
    s = relevances/(z+1e-9)
    positive = np.matmul(positiveWeights,s)

    z = np.matmul(np.transpose(negativeWeights),activations)
    s = relevances/(z-1e-9)
    negative = np.matmul(negativeWeights,s)

    relevances_current = activations*(alpha*positive - beta*negative)
    return relevances_current

def propagate_fully_to_conv(relevances, weights, activations, alpha):
    out_shape = activations.shape
    relevances = propagate_fully_connected(relevances, weights, activations.flatten(), alpha)
    return relevances.reshape(out_shape)


def propagate_conv(net, relevances, activations, weightsLayer, alpha):
    beta = alpha - 1

    positiveWeights = np.maximum(net.get_weights(weightsLayer), 1e-9)
    negativeWeights = np.minimum(net.get_weights(weightsLayer), -1e-9)

    z = forward(activations, positiveWeights, net.get_activations(weightsLayer).shape)
    s = relevances/z
    positive = backprop(s, positiveWeights, activations)

    z = forward(activations, negativeWeights, net.get_activations(weightsLayer).shape)
    s = relevances/z
    negative = backprop(s, negativeWeights, activations)

    return activations*(alpha*positive - beta*negative)

def propagate_first_conv(net, relevances, activations, weightsLayer, h, l):
    positiveWeights = np.maximum(net.get_weights(weightsLayer), 0)
    negativeWeights = np.minimum(net.get_weights(weightsLayer), 0)
    weights = net.get_weights(weightsLayer)

    X,L,H = activations,0*activations+l,0*activations+h

    z = forward(X, weights, net.get_activations(weightsLayer).shape) - forward(L, positiveWeights, net.get_activations(weightsLayer).shape) - forward(H, negativeWeights, net.get_activations(weightsLayer).shape)+1e-9
    s = relevances/z

    return X*backprop(s, weights, X) - L*backprop(s, positiveWeights, L) - H*backprop(s, negativeWeights, H)

def forward(x, w, shape):
    if len(x.shape) == 3:
        x = x.reshape((1,)+x.shape)
    x_col = im2col.im2col_indices(x, w.shape[2], w.shape[3])
    w_col = w.reshape(w.shape[0],w.shape[1]*w.shape[2]*w.shape[3])

    out = np.matmul(w_col,x_col)
    out = out.reshape((shape[0], shape[1], shape[2], 1))
    out = out.transpose(3, 0, 1, 2)
    return out

def backprop(s, w, x):
    s_reshaped = s
    if len(s.shape) == 3:
        s_reshaped = np.zeros(shape=(1, s.shape[0],s.shape[1],s.shape[2]))
        s_reshaped[0] = s
    s_reshaped = np.transpose(s_reshaped, (1,2,3,0))
    s_reshaped = s_reshaped.reshape((s_reshaped.shape[0],s_reshaped.shape[1]*s_reshaped.shape[2]*s_reshaped.shape[3]))

    x = x.reshape(tuple([1]+list(x.shape)))

    x_col = im2col.im2col_indices(x, w.shape[2], w.shape[3])

    dW = np.matmul(s_reshaped, np.transpose(x_col))
    dW = dW.reshape(w.shape)
    W_reshape = w.reshape((w.shape[0],w.shape[1]*w.shape[2]*w.shape[3]))
    dX_col = np.matmul(np.transpose(W_reshape), s_reshaped)
    dX = im2col.col2im_indices(dX_col, x.shape, w.shape[2], w.shape[3])
    return dX[0]

def propagate_pooling(net, relevances, activations, poolLayer, k):
    """Calculates the layer-wise relevance propagations for a given pooling layer
    inputs
    relevances: relevances of higher layer
    activations: activations for current layer
    output
    relevances of current layer
    """
    z = forwardMax(activations, k, net.get_activations(poolLayer).shape)+1e-9
    s = relevances/z
    c = backwardMax(s, activations, k)
    relevances = activations*c

    return relevances

def forwardMax(x,k, shape):
    x_reshaped = x.reshape((1,)+x.shape)
    x_reshaped = x_reshaped.reshape(x_reshaped.shape[1], 1, x_reshaped.shape[2], x_reshaped.shape[3])
    x_col = im2col.im2col_indices(x_reshaped, k, k, padding=0, stride=k)

    max_idx = np.argmax(x_col, axis=0)

    out = x_col[max_idx, range(max_idx.size)]

    out = out.reshape(shape[1], shape[2], 1, shape[0])

    out = out.transpose(2, 3, 0, 1)
    return out[0]

def backwardMax(s, x, k):
    x_reshaped = x.reshape((1,)+x.shape)
    x_reshaped = x_reshaped.reshape(x_reshaped.shape[1], 1, x_reshaped.shape[2], x_reshaped.shape[3])

    x_col = im2col.im2col_indices(x_reshaped, k, k, padding=0, stride=k)

    max_idx = np.argmax(x_col, axis=0)

    dX_col = np.zeros_like(x_col)

    s = s.reshape((1,)+s.shape)
    dout_flat = s.transpose(2, 3, 0, 1).ravel()
    dX_col[max_idx, range(max_idx.size)] = dout_flat

    dX = im2col.col2im_indices(dX_col, (x.shape[0],1,x.shape[1],x.shape[2]), k, k, padding=0, stride=k)

    dX = dX.reshape(x.shape)
    return dX

def calculate_lrp_heatmap(net, img):
    """Calculates the layer-wise relevance propagations for a given network and image
    inputs
    net: relevances of higher layer
    activations: activations for current layer
    output
    relevances of current layer
    """
    layer_names = net.get_layer_names()
    predictions = net.predict(img)
    prediction = np.argmax(np.mean(predictions, axis=0))
    relevances = np.zeros(predictions[0].shape)
    relevances[prediction] = 1
    l = np.amin(img)
    h = np.amax(img)
    alpha = 2
    print("Using alpha " + str(alpha) + " and beta " + str(alpha-1))
    print(prediction)
    layer_names = net.get_layer_names()
    layer_names.reverse()

    for index in range(len(layer_names)-1):
        name = layer_names[index]
        next_layer = layer_names[index+1]
        layer_type = net.get_layer_type(name)

        if layer_type == 'Pooling':
            kernel = net.get_kernel_size(name)
            relevances = propagate_pooling(net, relevances, net.get_activations(next_layer), name, kernel)
        elif layer_type == 'InnerProduct':
            next_layer_type = net.get_layer_type(next_layer)
            if next_layer_type != 'InnerProduct' :
                relevances = propagate_fully_to_conv(relevances, np.transpose(net.get_weights(name)), net.get_activations(next_layer), alpha)
            else:
                relevances = propagate_fully_connected(relevances, np.transpose(net.get_weights(name)), net.get_activations(next_layer), alpha) # relevances of fc6
        elif layer_type == 'Convolution' and net.get_layer_type(next_layer) == 'Input':
            relevances = propagate_first_conv(net, relevances, net.get_activations(next_layer), name, h, l)
        elif layer_type == 'Convolution':
            relevances =  propagate_conv(net, relevances, net.get_activations(next_layer), name, alpha)

    relevances =  np.mean(relevances.transpose(1,2,0), 2)

    return relevances
