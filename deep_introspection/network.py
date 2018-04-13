import caffe
import tensorflow as tf
from caffe.proto import caffe_pb2
from google.protobuf import text_format
import numpy as np

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
        if not self.predicted:
            return None
        return self.net.blobs[layer].data[0]

    def get_layer_type(self, layer):
        if layer == 'data':
            return "Input"
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

class TensorFlowNet:
    sess = None
    img = None
    predicted = False

    def __init__(self, meta, dir):
        self.sess = tf.Session()
        new_saver = tf.train.import_meta_graph(meta)
        new_saver.restore(self.sess, tf.train.latest_checkpoint(dir))

    def __del__(self):
        self.sess.close()
        
    def get_weights(self, layer):
        weights = self.sess.graph.get_tensor_by_name(layer+'/weights:0')
        weights = weights.eval(session=self.sess)
        if len(weights.shape) == 4:
            return weights.transpose(3, 2, 1, 0)
        return weights.transpose()

    def get_activations(self, layer):
        if not self.predicted:
            return None

        placeholder = list(filter(lambda x: x.type == 'Placeholder', self.sess.graph.get_operations()))[0]
        placeholder = placeholder.values()

        probs = self.sess.graph.get_operation_by_name('Softmax').values()

        layer_type = self.get_layer_type(layer)
        if layer_type == 'Convolution' or layer_type == 'Pooling':
            layer = self.sess.graph.get_operation_by_name(layer).values()
        else:
            layer = self.sess.graph.get_operation_by_name(layer+'/Relu').values()

        layer = self.sess.run(layer, feed_dict={placeholder: [self.img]})[0][0]

        if layer_type == 'Convolution' or layer_type == 'Pooling':
            return layer.transpose(2, 0, 1)

        return layer


    def get_layer_type(self, layer):
        try:
            self.sess.graph.get_operation_by_name(layer+'/Conv2D')
            return "Convolution"
        except:
            try:
                self.sess.graph.get_operation_by_name(layer+'/MatMul')
                return "InnerProduct"
            except:
                if self.sess.graph.get_operation_by_name(layer).type == 'Placeholder':
                    return "Input"
                else:
                    return "Pooling"


    def get_kernel_size(self, layer):
        return [int(a) for a in list(filter(lambda n: n.name == layer, self.sess.graph.as_graph_def().node))[0].attr['ksize'].list.i][1]

    def predict(self, img):
        placeholder = list(filter(lambda x: x.type == 'Placeholder', self.sess.graph.get_operations()))[0]
        placeholder = placeholder.values()

        probs = self.sess.graph.get_operation_by_name('Softmax').values()

        self.img = np.array([img])
        self.predicted = True
        prob = self.sess.run(probs, feed_dict={placeholder: [self.img]})[0]

        return prob

    def get_layer_names(self):
        layer_names = list(map(lambda x: x.name, filter(lambda x: x.type == 'Conv2D' or x.type=='MatMul' or x.type=='MaxPool' or x.type=='AvgPool' or x.type=='Placeholder', self.sess.graph.get_operations())))
        layer_names = list(map(lambda x: x.split('/')[0], layer_names))
        return layer_names
