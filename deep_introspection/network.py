import caffe


class CaffeNet:
    net = None
    predicted = False

    def __init__(self, architecture, weights):
        self.net = caffe.Classifier(architecture, weights, caffe.TEST,channel_swap=(2,1,0))

    def get_weights(self, layer):
        return self.net.params[layer][0].data

    def get_activations(self, layer):
        if self.predicted == False:
            return None
        return self.net.blobs[layer].data[0]

    def predict(self, img):
        self.net.image_dims = img[1]
        self.net.predict([img[0]])
        self.predicted = True
        return self.net.blobs['prob'].data
