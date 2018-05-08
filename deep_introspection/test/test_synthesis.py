from deep_introspection import network, synthesis, utils
import numpy as np
import matplotlib.pyplot as plt

# def test_synthesise_loss_is_low():
#     net = network.CaffeNet('deep_introspection/test/VGG.prototxt', 'deep_introspection/test/VGG_ILSVRC_16_layers.caffemodel')
#     img, offset, resFac, newSize = utils.imgPreprocess(img_path='deep_introspection/test/cat.jpg')
#
#     net.set_new_size(newSize)
#     net.predict(img)
#
#     layer = net.get_layer_names()[-1]
#     print("Testing layer " + layer)
#
#     target_rep = net.get_activations(layer)
#
#     solution, loss = synthesis.synthesise(net, target_rep)
#     net.set_new_size(solution.shape[:2])
#     net.predict(solution)
#
#     plt.imshow(np.maximum(solution, 0)/255)
#     plt.show()
#     print(loss)
#
#     assert(solution.shape == (224,224,3))
#     assert(synthesis.loss(net.get_activations(layer), target_rep) < 0.01)

def test_boundary():

    net = network.CaffeNet('deep_introspection/test/VGG.prototxt', 'deep_introspection/test/VGG_ILSVRC_16_layers.caffemodel')
    img, offset, resFac, newSize = utils.imgPreprocess(img_path='deep_introspection/test/cat.jpg')

    net.set_new_size(newSize)

    solution, loss = synthesis.synthesise_boundary(net, img, 200, 150, 100, 50)
    net.predict(solution)

    plt.imshow(np.maximum(solution, 0)/255)
    plt.show()
    print(loss)

    assert(solution.shape == (224,224,3))
    assert(synthesis.loss(net.get_activations(layer), target_rep) < 0.01)
