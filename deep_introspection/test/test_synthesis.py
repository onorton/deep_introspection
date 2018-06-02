from deep_introspection import network, synthesis, utils
import numpy as np
import matplotlib.pyplot as plt

def test_synthesise_loss_is_low():
    net = network.CaffeNet('deep_introspection/test/VGG.prototxt', 'deep_introspection/test/VGG_ILSVRC_16_layers.caffemodel')
    img, offset, resFac, newSize = utils.imgPreprocess(img_path='deep_introspection/test/cat.jpg')
    net.set_new_size(newSize)
    net.predict(img)

    layer = net.get_layer_names()[-1]
    print("Testing layer " + layer)

    target_rep = net.get_activations(layer)

    solution, loss = synthesis.synthesise(net, target_rep)
    net.set_new_size(solution.shape[:2])
    net.predict(solution)

    plt.imshow(np.maximum(solution, 0)/255)
    plt.show()
    print(loss)
    print(synthesis.loss(net.get_activations(layer), target_rep))
    assert(solution.shape == (224,224,3))
    assert(synthesis.loss(net.get_activations(layer), target_rep) < 0.1)

def test_boundary():

    net = network.CaffeNet('deep_introspection/test/VGG.prototxt', 'deep_introspection/test/VGG_ILSVRC_16_layers.caffemodel')
    img, offset, resFac, newSize = utils.imgPreprocess(img_path='deep_introspection/test/cat.jpg')

    net.set_new_size(newSize)

    solution, loss = synthesis.synthesise_boundary(net, img, 160, 75, 120, 0)
    net.predict(solution)
    mean = np.array([103.939, 116.779, 123.68])
    solution[:,:,2] += mean[0]
    solution[:,:,1] += mean[1]
    solution[:,:,0] += mean[2]


    plt.imshow(np.maximum(solution, 0)/255)
    plt.show()
    print(loss)

    assert(solution.shape == (224,224,3))
    assert(synthesis.loss(net.get_activations(layer), target_rep) < 0.01)
