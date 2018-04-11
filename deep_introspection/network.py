import caffe
from caffe.proto import caffe_pb2
from google.protobuf import text_format

class CaffeNet:
    net = None
    layers = None
    predicted = False

    def __init__(self, architecture, weights):
        self.net = caffe.Classifier(architecture, weights, caffe.TEST,channel_swap=(2,1,0))

        parsible_net = caffe_pb2.NetParameter()
        text_format.Merge(open(architecture).read(), parsible_net)

        self.layers = parsible_net.layers

    def get_weights(self, layer):
        return self.net.params[layer][0].data

    def get_activations(self, layer):
        if self.predicted == False:
            return None
        return self.net.blobs[layer].data[0]

    def get_layer_type(self, layer):
        return self.net.layers[list(self.net._layer_names).index(layer)].type

    def get_kernel_size(self, layer):
        return [x for x in self.layers if x.name == layer][0].pooling_param.kernel_size


    def predict(self, img):
        self.net.predict([img])
        self.predicted = True
        return self.net.blobs['prob'].data

    def set_new_size(self, new_size):
        self.net.image_dims = new_size


    def get_layer_names(self) :
        """Gets the layer names of relevant networks in order
        net: caffe network
        output
        list of layer names
        """

        layer_names = ['data']

        for i in range(len(list(self.net._layer_names))):
            if self.net.layers[i].type == 'Convolution' or self.net.layers[i].type == 'Pooling' or self.net.layers[i].type == 'InnerProduct':
                layer_names.append(self.net._layer_names[i])

        return layer_names
