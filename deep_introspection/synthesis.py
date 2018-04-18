import numpy as np

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

    step_size = 0.01

    for i in range(100):
        x -= step_size * x
        print(loss(net.get_activations(layer), rep))
    return x



def loss(rep, target):
    """
    Calculates loss which in this case is the euclidean distance

    inputs
    rep: the test representation
    target: the representation to approximate

    """
    return np.linalg.norm(rep-target)**2
