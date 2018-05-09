import numpy as np
from deep_introspection import im2col, lrp
import matplotlib.pyplot as plt

alpha = 6
beta = 2
m = 0.9
C = 1
B = 80
V = B/6.5
l = 1/(224*224*B**alpha)
l_tv = 1/(224*224*V**beta)


def synthesise_boundary(net, img, xmax, ymax, xmin=0,ymin=0):
    x = 2*B*np.random.uniform(size=net.input_shape())

    x[ymin:ymax+1,xmin:xmax+1,:] = img[ymin:ymax+1,xmin:xmax+1,:]
    net.set_new_size(net.input_shape())
    net.predict(x)

    layer = net.get_layer_names()[-1]
    target = net.get_activations(layer)

    return synthesise(net, target)


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
    x = 2*B*np.random.uniform(size=net.input_shape())

    layer = net.get_layer_names()[-1]
    net.set_new_size(x.shape[:2])

    lr = 0.01*(B**2)/alpha
    mu = 0
    g = 0
    prev_x = np.copy(x)

    net.predict(x)
    rep = net.get_activations(layer)

    rep_loss = loss(rep, target)
    prev_loss = rep_loss + regularised(x)

    print("Initial total loss: " + str(prev_loss))
    print("Initial loss: " + str(rep_loss))

    iterations = 400
    for i in range(iterations):
        # adagrad
        grad = C*gradient(net, rep-target) + l*norm_grad(x) + l_tv*tv_grad(x)
        g = m*g + grad**2
        lr = 1/(1/lr + g**0.5)
        mu = m*mu -lr * grad
        x += mu


        net.predict(x)
        rep = net.get_activations(layer)
        rep_loss = loss(rep, target)


        total_loss = rep_loss + regularised(x)
        print("Iteration " + str(i))
        print("Total loss:" + str(total_loss) + ", TV loss: " + str(tv(x)))
        print("Loss: " + str(rep_loss))

        if (i+1)%100 == 0:
            plt.imshow(np.maximum(x, 0)/2*B)
            plt.show()

    return x, total_loss

def regularised(x):
    norm = np.sum((np.sum(x**2, 2)**(alpha/2)))
    print(l*norm, l_tv*tv(x))
    return l*norm + l_tv*tv(x)

def norm_grad(x):
    summed = alpha*(np.sum(x**2, axis=2))**(alpha/2-1)
    return (summed.T*x.T).T


def tv(x):
    shift_w = np.zeros(x.shape)
    shift_w[:-1,:] = x[1:,:]
    #shift_w[-1,:] = x[-1,:]


    shift_h = np.zeros(x.shape)
    shift_h[:,:-1] = x[:,1:]
    #shift_h[:,-1] = x[:,-1]


    tv = np.sum((shift_w-x)**2 + (shift_h-x)**2)
    return tv

def tv_grad(x):

    shift_w = np.zeros(x.shape)
    shift_w[:-1,:] = x[1:,:]
    #shift_w[-1,:] = x[-1,:]

    shift_w_back = np.zeros(x.shape)
    shift_w_back[1:,:] = x[:-1,:]
    #shift_w_back[0,:] = x[0,:]

    shift_h = np.zeros(x.shape)
    shift_h[:,:-1] = x[:,1:]
    #shift_h[:,-1] = x[:,-1]

    shift_h_back = np.zeros(x.shape)
    shift_h_back[:,1:] = x[:,:-1]
    #shift_h_back[:,0] = x[:,0]

    grad = 2*((x-shift_h_back)+(x-shift_w_back)-(shift_h-x)-(shift_w-x))

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
    layer_names = net.get_layer_names()

    grad = 2*out
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
            without_relu = forward(net.get_activations(next_layer), net.get_weights(name), net.get_biases(name), net.get_activations(name).shape)[0]
            grad[without_relu <= 0] = 0
            grad = backprop(grad, net.get_weights(name), net.get_activations(next_layer))

    return grad.T

def forward(x, w, b, shape):
    if len(x.shape) == 3:
        x = x.reshape((1,)+x.shape)
    w = w.transpose(0, 1, 3, 2)

    x_col = im2col.im2col_indices(x, w.shape[2], w.shape[3])
    w_col = w.reshape(w.shape[0],-1)

    out = ((w_col @ x_col).T + b.T).T
    out = out.reshape((shape[0], shape[1], shape[2], 1))
    out = out.transpose(3, 0, 2, 1)
    return out

def backprop(s, w, x):
    s_reshaped = s
    if len(s.shape) == 3:
        s_reshaped = s.reshape(tuple([1]+list(s.shape)))
    s_reshaped = s_reshaped.transpose(1,3,2,0)
    s_reshaped = s_reshaped.reshape(s_reshaped.shape[0],-1)

    w = w.transpose(0, 1, 3, 2)

    x = x.reshape(tuple([1]+list(x.shape)))

    W_reshape = w.reshape(w.shape[0],-1)
    dX_col = W_reshape.T @ s_reshaped
    dX = im2col.col2im_indices(dX_col, x.shape, w.shape[2], w.shape[3])
    return dX[0].transpose(0,2,1)
