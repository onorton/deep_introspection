from deep_introspection import network, synthesis, utils
import numpy as np
import matplotlib.pyplot as plt

def test_synthesise_loss_is_low():
    net = network.CaffeNet('deep_introspection/test/VGG.prototxt', 'deep_introspection/test/VGG_ILSVRC_16_layers.caffemodel')
    img, offset, resFac, newSize = utils.imgPreprocess(img_path='deep_introspection/test/cat.jpg')

    net.set_new_size(newSize)
    print(np.argmax(np.mean(net.predict(img), axis=0)))

    layer = net.get_layer_names()[-1]
    print("Testing layer " + layer)

    target_rep = net.get_activations(layer)

    solution, loss = synthesis.synthesise(net, target_rep,layer)
    net.set_new_size(solution.shape[:2])
    net.predict(solution)

    assert(solution.shape == (224,224,3))
    assert(synthesis.loss(net.get_activations(layer), target_rep) < 0.1)

def test_boundary():

    net = network.CaffeNet('deep_introspection/test/VGG.prototxt', 'deep_introspection/test/VGG_ILSVRC_16_layers.caffemodel')
    img, offset, resFac, newSize = utils.imgPreprocess(img_path='deep_introspection/test/cat.jpg')

    net.set_new_size(newSize)

    layer = net.get_layer_names()[-2]
    solution, loss = synthesis.synthesise_boundary(net, img, layer,  185, 120, 140, 95)

    assert(solution.shape == (224,224,3))

def test_boundary_synthesis():

    net = network.CaffeNet('deep_introspection/test/VGG.prototxt', 'deep_introspection/test/VGG_ILSVRC_16_layers.caffemodel')

    target = np.zeros(1000)
    target[285] = 0.5
    target[7] = 0.5
    solution, loss = synthesis.synthesise(net, target, 'prob')

    assert(solution.shape == (224,224,3))
