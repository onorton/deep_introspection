from deep_introspection import network, utils
from scipy.misc import imread, imresize

net = network.CaffeNet('deep_introspection/test/VGG.prototxt', 'deep_introspection/test/VGG_ILSVRC_16_layers.caffemodel')
img, offset, resFac, newSize = utils.imgPreprocess(img_path='deep_introspection/test/cat.jpg')
net.set_new_size(newSize)

tfNet = network.TensorFlowNet('deep_introspection/test/vgg16.meta', './deep_introspection/test/')

img1 = imread('deep_introspection/test/cat.jpg', mode='RGB')
img1 = imresize(img1, (224, 224))

def test_caffe_conv_weights_correct_shape():
    weights = net.get_weights('conv1_1')
    assert(weights.shape == (64,3,3,3))

def test_caffe_fc_weights_correct_shape():
    weights = net.get_weights('fc8')
    assert(weights.shape == (1000,4096))

def test_caffe_activations_correct_shape():
    net.predict(img)
    activations = net.get_activations('conv1_1')
    assert(activations.shape == (64,224,224))

def test_caffe_no_activations_if_not_predicted():
    net = network.CaffeNet('deep_introspection/test/VGG.prototxt', 'deep_introspection/test/VGG_ILSVRC_16_layers.caffemodel')
    assert(net.get_activations('fc7') == None)

def test_caffe_predictions_sensible():
    assert(net.predict(img).shape == (10, 1000))

def test_caffe_layers_found_should_be_in_order():
    layer_names = net.get_layer_names()
    assert(layer_names == ['data','conv1_1','conv1_2','pool1','conv2_1','conv2_2','pool2','conv3_1','conv3_2','conv3_3','pool3','conv4_1','conv4_2','conv4_3','pool4','conv5_1','conv5_2','conv5_3','pool5','fc6','fc7','fc8'])

def test_caffe_retrieves_layer_type():
    assert(net.get_layer_type('pool5') == 'Pooling')

def test_caffe_retrieves_input_layer_type():
    assert(net.get_layer_type('data') == 'Input')

def test_caffe_retrieves_kernel_size():
    assert(net.get_kernel_size('pool5') == 2)

def test_tf_conv_weights_correct_shape():
    weights = tfNet.get_weights('conv5_3')
    print(weights.shape)
    assert(weights.shape==(512,512,3,3))

def test_tf_conv_weights_correct_shape_2():
    weights = tfNet.get_weights('conv1_1')
    assert(weights.shape==(64,3,3,3))

def test_tf_fc_weights_correct_shape():
    weights = tfNet.get_weights('fc3')
    assert(weights.shape == (1000,4096))

def test_tf_predictions_sensible():
    assert(tfNet.predict(img1).shape == (1, 1000))

def test_tf_retrieves_kernel_size():
    assert(tfNet.get_kernel_size('pool4') == 2)

def test_tf_retrieves_pooling_layer_type():
    assert(tfNet.get_layer_type('pool4_1') == 'Pooling')

def test_tf_retrieves_convolution_layer_type():
    assert(tfNet.get_layer_type('conv1_1') == 'Convolution')

def test_tf_retrieves_fc_layer_type():
    assert(tfNet.get_layer_type('fc1') == 'InnerProduct')

def test_caffe_retrieves_input_layer_type():
    assert(tfNet.get_layer_type('Placeholder') == 'Input')

def test_tf_layers_found_should_be_in_order():
    layer_names = tfNet.get_layer_names()
    assert(layer_names == ['Placeholder','conv1_1','conv1_2','pool1','conv2_1','conv2_2','pool2','conv3_1','conv3_2','conv3_3','pool3','conv4_1','conv4_2','conv4_3','pool4','conv5_1','conv5_2','conv5_3','pool4_1','fc1','fc2','fc3'])

def test_tf_conv_activations_correct_shape():
    tfNet.predict(img1)
    activations = tfNet.get_activations('conv1_1')
    assert(activations.shape == (64,224,224))

def test_tf_fc_activations_correct_shape():
    tfNet.predict(img1)
    activations = tfNet.get_activations('fc2')
    assert(activations.shape == (4096,))

def test_tf_pool_activations_correct_shape():
    tfNet.predict(img1)
    activations = tfNet.get_activations('pool4_1')
    assert(activations.shape == (512,7,7))
