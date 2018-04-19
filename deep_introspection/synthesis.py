import numpy as np
from deep_introspection import lrp

def synthesise(net, rep):
    """
    Find an image whose representation in the network is as close as possible
    to the representation given.

    inputs
    net: the network that is being used
    rep: the representation that is trying to be inverted
    in this case, the layer before the final softmax layer
    output
    An image as a numpy array
    """

    x = 256*np.random.uniform(size=net.input_shape())
    layer = net.get_layer_names()[-2]
    net.set_new_size(x.shape[:2])

    step_size = 0.00001

    for i in range(20):
        net.predict(x)
        rep_loss = loss(net.get_activations(layer), rep)
        grad = gradient(net, rep_loss)
        x -= step_size * grad
        print(rep_loss)
    return x



def loss(rep, target):
    """
    Calculates loss which in this case is the euclidean distance

    inputs
    rep: the test representation
    target: the representation to approximate

    """
    return np.linalg.norm(rep-target)**2


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
