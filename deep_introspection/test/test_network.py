from deep_introspection import network, utils

net = network.CaffeNet('deep_introspection/test/VGG.prototxt', 'deep_introspection/test/VGG_ILSVRC_16_layers.caffemodel')
img, offset, resFac, newSize = utils.imgPreprocess(img_path='deep_introspection/test/cat.jpg')

def test_caffe_weights_correct_shape():
    weights = net.get_weights('conv1_1')
    assert(weights.shape == (64,3,3,3))

def test_caffe_activations_correct_shape():
    net.predict((img,newSize))
    activations = net.get_activations('conv1_1')
    assert(activations.shape == (64,224,224))

def test_caffe_no_activations_if_not_predicted():
    net = network.CaffeNet('deep_introspection/test/VGG.prototxt', 'deep_introspection/test/VGG_ILSVRC_16_layers.caffemodel')
    assert(net.get_activations('fc7') == None)

def test_caffe_predictions_sensible():
    assert(net.predict((img, newSize)).shape == (10, 1000))
