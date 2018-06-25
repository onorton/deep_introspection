import numpy as np
from deep_introspection import im2col, lrp
import matplotlib.pyplot as plt
from scipy.misc import imread, imresize
from skimage import util

alpha = 6
beta = 2
m = 0.9
B = 80
B_plus = 2*B

V = B/6.5
C = 1
l = 0
l_tv = 0

def synthesise_boundary(net, img, layer, xmax, ymax, xmin=0,ymin=0):
    x = B_plus*np.random.uniform(size=net.input_shape())-B
    plt.imshow((img+128)/255)
    plt.show()
    height = ymax-ymin+1
    width = xmax-xmin+1

    if height % 2 == 1:
        height += 1
        ymax += 1
    if width % 2 == 1:
        width += 1
        xmax += 1

    x[net.input_shape()[0]//2-height//2:net.input_shape()[0]//2+height//2,net.input_shape()[1]//2-width//2:net.input_shape()[1]//2+width//2,:] = img[ymin:ymax+1,xmin:xmax+1,:]

    mod_img = np.copy(img)

    mean = np.array([103.939, 116.779, 123.68])
    mod_img[:,:,2] += mean[0]
    mod_img[:,:,1] += mean[1]
    mod_img[:,:,0] += mean[2]

    print(ymin,ymax,xmin,xmax)
    x = imresize(mod_img[ymin:ymax+1,xmin:xmax+1,:],net.input_shape()[:2]).astype('float64')
    plt.imshow(x/255)
    plt.show()

    net.set_new_size(net.input_shape()[:2])
    print(np.mean(net.predict(x), axis=0).argsort()[-5:][::-1])
    # mean = np.array([103.939, 116.779, 123.68])
    # x[:, :, 0] += mean[2]
    # x[:, :, 1] += mean[1]
    # x[:, :, 2] += mean[0]

    target = net.get_activations(layer)
    print(target.shape)
    return synthesise(net, target, layer)


def synthesise(net, target, layer):
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


    x = 2*np.random.uniform(size=net.input_shape())-1

    for i in range(x.shape[2]):
         t = np.percentile(x[:,:,i], 95)
         x[:,:,i] = x[:,:,i]/t * B/(x.shape[2]**0.5)

    net.set_new_size(x.shape[:2])

    initial_lr = 0.01*(B**2)/alpha
    g = 0
    mu = 0

    net.predict(x)

    rep = net.get_activations(layer)
    rep_loss = loss(rep, target)
    prev_loss = C*rep_loss + regularised(x)

    print("Initial total loss: " + str(prev_loss))
    print("Initial loss: " + str(rep_loss))


    iterations = 50
    for i in range(iterations):

        #clip pixel intensities
        pixel_intensities = np.sum(x**2, axis=2)**0.5
        x[pixel_intensities > B_plus] = (x[pixel_intensities > B_plus].T/(pixel_intensities[pixel_intensities > B_plus].T/B_plus)).T

        # adagrad
        loss_grad = C*gradient(net, layer, rep-target)/np.linalg.norm(target)**2
        grad = loss_grad + l*norm_grad(x) + l_tv*tv_grad(x)

        g = m*g + grad**2
        lr = 1/(1/initial_lr+g**0.5)
        mu = m*mu - lr * grad
        x += B*mu

        net.predict(x)
        rep = net.get_activations(layer)
        prev_loss = rep_loss
        rep_loss = loss(rep, target)
        total_loss = C*rep_loss + regularised(x)

        print("Iteration " + str(i) + ": " + str(np.mean(lr)))
        print("Total loss:" + str(total_loss) + ", TV loss: " + str(tv(x)))
        print("Loss: " + str(rep_loss) + " Change: " + str(rep_loss-prev_loss))

    return x, rep_loss

def regularised(x):
    norm = np.sum((np.sum(x**2, 2)**(alpha/2)))
    print(l*norm, l_tv*tv(x), "Mean intensity: " + str(np.mean(np.sum(x**2, axis=2)**0.5)))
    return l*norm + l_tv*tv(x)

def norm_grad(x):
    summed = alpha*(np.sum(x**2, axis=2))**(alpha/2-1)
    return (summed.T*x.T).T


def tv(x):
    shift_w = np.zeros(x.shape)
    shift_w[:-1,:] = x[1:,:]

    shift_h = np.zeros(x.shape)
    shift_h[:,:-1] = x[:,1:]


    tv = np.sum((shift_w-x)**2 + (shift_h-x)**2)
    return tv

def tv_grad(x):

    shift_w = np.zeros(x.shape)
    shift_w[:-1,:] = x[1:,:]

    shift_w_back = np.zeros(x.shape)
    shift_w_back[1:,:] = x[:-1,:]

    shift_h = np.zeros(x.shape)
    shift_h[:,:-1] = x[:,1:]

    shift_h_back = np.zeros(x.shape)
    shift_h_back[:,1:] = x[:,:-1]

    grad = 2*((x-shift_h_back)+(x-shift_w_back)-(shift_h-x)-(shift_w-x))

    return grad

def loss(rep, target):
    """
    Calculates loss which in this case is the euclidean distance

    inputs
    rep: the test representation
    target: the representation to approximate

    """
    return np.linalg.norm(rep-target)**2/np.linalg.norm(target)**2
    #return np.linalg.norm(rep)

def gradient(net, layer, out):
    """
    Computes the gradient of the given out

    """
    return net.backward(layer, 2*out)
