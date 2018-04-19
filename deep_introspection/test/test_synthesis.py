from deep_introspection import network, synthesis, utils
import numpy as np
import matplotlib.pyplot as plt

def test_synthesise_loss_is_low():
    net = network.CaffeNet('deep_introspection/test/VGG.prototxt', 'deep_introspection/test/VGG_ILSVRC_16_layers.caffemodel')
    img, offset, resFac, newSize = utils.imgPreprocess(img_path='deep_introspection/test/cat.jpg')
    net.set_new_size(newSize)
    net.predict(img)

    layer = net.get_layer_names()[-2]

    target_rep = net.get_activations(layer)

    solution = synthesis.synthesise(net, target_rep)

    net.set_new_size(solution.shape[:2])
    net.predict(solution)

    plt.imshow(np.maximum(solution, 0)/256)
    plt.show()
    print(synthesis.loss(net.get_activations(layer), target_rep)/solution.flatten().shape[0])

    assert(solution.shape == (224,224,3))
    assert(synthesis.loss(net.get_activations(layer), target_rep)/solution.flatten().shape[0] < 0.01)
