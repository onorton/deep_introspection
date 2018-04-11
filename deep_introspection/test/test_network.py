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

def test_layers_found_should_be_in_order():
    layer_names = net.get_layer_names()
    assert(layer_names == ['data','conv1_1','conv1_2','pool1','conv2_1','conv2_2','pool2','conv3_1','conv3_2','conv3_3','pool3','conv4_1','conv4_2','conv4_3','pool4','conv5_1','conv5_2','conv5_3','pool5','fc6','fc7','fc8'])
