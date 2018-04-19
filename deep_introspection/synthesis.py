import numpy as np
from deep_introspection import lrp
alpha = 6

def synthesise(net, rep):
    """
    Find an image whose representation in the network is as close as possible
    to the representation given.

    inputs
    net: the network that is being used
    rep: the representation that is trying to be inverted
    in this case, the layer before the final softmax layer
    output
    An image as a numpy array, total loss
    """

    x = 256*np.random.uniform(size=net.input_shape())-128
    layer = net.get_layer_names()[-2]
    net.set_new_size(x.shape[:2])

    step_size = 0.1
    sigma = 0.3
    l = sigma/(x.shape[0]*x.shape[1]*(128**alpha))

    for i in range(300):
        if i % 100 == 0:
            step_size /= 10
        net.predict(sigma*x)
        rep_loss = loss(net.get_activations(layer), rep)
        grad = gradient(net, rep_loss)
        print(rep_loss)
        print(rep_loss+regularised(x))
        x -= step_size * (grad + l*alpha*x**(alpha-1))
        #x -= step_size * grad

    return x+128, (rep_loss + regularised(x))

def regularised(x):
    return np.sum(x**alpha)

def loss(rep, target):
    """
    Calculates loss which in this case is the euclidean distance

    inputs
    rep: the test representation
    target: the representation to approximate

    """
    return np.linalg.norm(rep-target)**2/(np.linalg.norm(target)**2)


def gradient(net, out):
    """
    Computes the gradient of the given out


    """
    layer_names = net.get_layer_names()[:-1]
    layer = net.get_layer_names()[-2]

    grad = (out/net.get_activations(layer).flatten().shape[0])*np.ones(net.get_activations(layer).shape)
    layer_names.reverse()

    for index in range(len(layer_names)-1):
        name = layer_names[index]
        next_layer = layer_names[index+1]
        layer_type = net.get_layer_type(name)

        if layer_type == 'Pooling':
            kernel = net.get_kernel_size(name)
            grad = lrp.backwardMax(grad, net.get_activations(next_layer), kernel)
        elif layer_type == 'InnerProduct':
            next_layer_type = net.get_layer_type(next_layer)
            grad = np.matmul(np.transpose(net.get_weights(name)),grad)
            if next_layer_type != 'InnerProduct' :
                grad = grad.reshape(net.get_activations(next_layer).shape)
            else:
                grad = np.matmul(np.transpose(net.get_weights(name)),grad)
        elif layer_type == 'Convolution':
            grad = lrp.backprop(grad, net.get_weights(name), net.get_activations(next_layer))
    return grad.transpose(1,2,0)
