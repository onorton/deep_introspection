import numpy as np
from deep_introspection import lrp
import matplotlib.pyplot as plt

alpha = 6
beta = 2
l_tv = 10
l = 8e-10
m = 0.9

def synthesise(net, target):
    """
    Find an image whose representation in the network is as close as possible
    to the representation given.

    inputs
    net: the network that is being used
    target: the representation that is trying to be inverted
    in this case, the layer before the final softmax layer
    output
    An image as a numpy array, total loss
    """
    x = 256*np.random.uniform(size=net.input_shape())-128
    layer = net.get_layer_names()[-2]
    net.set_new_size(x.shape[:2])

    lr = 0.01
    mu = 0
    prev_x = np.copy(x)
    net.predict(x)
    rep_loss = loss(net.get_activations(layer), target)

    # prev_loss = rep_loss + regularised(x)
    prev_loss = rep_loss + regularised(x)

    print("Initial loss: " + str(rep_loss))
    iterations = 400
    for i in range(iterations):
        grad = gradient(net, net.get_activations(layer)-target)
        delta = grad + l*alpha*x**(alpha-1) + l_tv*tv_grad(x)
        #delta = grad
        old_mu = np.copy(mu)
        mu = -lr * delta
        x += mu

        net.predict(x)
        rep_loss = loss(net.get_activations(layer), target)
        total_loss = rep_loss + regularised(x)
        print("Iteration " + str(i) +": " + str(lr))
        print("Total loss:" + str(total_loss))
        print("Loss: " + str(rep_loss))

        if total_loss <= prev_loss:
            lr *= 2
            prev_x = np.copy(x)
            prev_loss = total_loss
        else:
            lr /= 2
            x = np.copy(prev_x)
            mu = old_mu

    print(x.flatten())
    return x+128, (rep_loss + regularised(x))

def regularised(x):

    norm = np.sum(x**alpha)

    shift_w = np.zeros(x.shape)
    shift_w[:-1,:] = x[1:,:]
    shift_w[-1,:] = x[-1,:]


    shift_h = np.zeros(x.shape)
    shift_h[:,:-1] = x[:,1:]
    shift_h[:,-1] = x[:,-1]


    tv = np.sum((shift_w-x)**2 + (shift_h-x)**2)
    return l*norm + l_tv*tv

def tv_grad(x):

    shift_w = np.zeros(x.shape)
    shift_w[:-1,:] = x[1:,:]
    shift_w[-1,:] = x[-1,:]

    shift_w_back = np.zeros(x.shape)
    shift_w_back[1:,:] = x[:-1,:]
    shift_w_back[0,:] = x[0,:]

    shift_h = np.zeros(x.shape)
    shift_h[:,:-1] = x[:,1:]
    shift_h[:,-1] = x[:,-1]

    shift_h_back = np.zeros(x.shape)
    shift_h_back[:,1:] = x[:,:-1]
    shift_h_back[:,0] = x[:,0]

    grad = -2*(shift_h-x)-2*(shift_w-x)+2*(x-shift_h_back)+2*(x-shift_w_back)

    return grad

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

    grad = 2*out
    #grad = (out/net.get_activations(layer).flatten().shape[0])*np.ones(net.get_activations(layer).shape)
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
            without_relu = np.matmul(net.get_weights(name),net.get_activations(next_layer).flatten())+net.get_biases(name)
            grad[without_relu <= 0] = 0
            grad = np.matmul(np.transpose(net.get_weights(name)),grad)
            if next_layer_type != 'InnerProduct' :
                grad = grad.reshape(net.get_activations(next_layer).shape)
        elif layer_type == 'Convolution':
            biases = (net.get_biases(name).T*np.ones(net.get_activations(name).shape).T).T
            without_relu = lrp.forward(net.get_activations(next_layer), net.get_weights(name),net.get_activations(name).shape)[0]+biases
            grad[without_relu <= 0] = 0
            grad = lrp.backprop(grad, net.get_weights(name), net.get_activations(next_layer))

    return grad.transpose(2,1,0)
