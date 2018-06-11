import numpy as np


def discriminative_locations_fully_connected(X, W, A):
    """Calculates outgoing discriminative locations
    inputs
    X: incoming discriminative locations from higher layer
    W: weights of higher layer
    A: activations at current layer
    output
    outgoing discriminative locations of current layer
    """
    # If previous layer is not fully connected
    for cr in range(5):
        if X[cr] != 0:
            layer_out = []
            data = np.squeeze(A[cr])
            param = W
            if (data.ndim == 3):
                shape = data.shape
                data = np.reshape(data, [param.shape[1], ])
                C = data*param
                for i in X[cr]:
                    position = np.argmax(C[i, :])
                    layer_out.append(np.unravel_index(position, shape))
            else:
                C = data*param
                for i in X[cr]:
                    num = np.sum(C[i, :] > 0)
                    layer_out.extend(np.argsort(C[i, :])[::-1][:num])
            X[cr] = list(set(layer_out))
    return X

def discriminative_locations_pool(X, A, K, S):
    for cr in range(5):
        if X[cr] != 0:
            layer_out = []
            for i in X[cr]:
                if not isinstance(i, tuple):
                    i = [i] + [0, 0]
                    # Getting the receptive region the pool operates on
                x = (S*i[1], S*i[1] + K)
                y = (S*i[2], S*i[2] + K)
                    # Getting most contributing x and y relative to the
                    # region being operated on
                blob = A[cr, i[0], x[0]:x[1], y[0]:y[1]]
                x1, y1 = np.unravel_index(np.argmax(blob), blob.shape)
                layer_out.append((i[0], x[0]+x1, y[0]+y1))
            X[cr] = list(set(layer_out))
    return X

def discriminative_locations_convolution(X, W, A, K, S, P):
    """Calculates outgoing discriminative locations
    inputs
    X: incoming discriminative locations from higher layer
    W: weights of higher layer
    A: activations at current layer
    K: kernel of higher layer
    S: stride of higher layer
    output
    outgoing discriminative locations of current layer
    """
    for cr in range(5):
        if X[cr] != 0:
            layer_out = []
            for i in X[cr]:
                x = (S*i[1], S*i[1] + K)
                y = (S*i[2], S*i[2] + K)
                if (P != 0):
                    data = np.lib.pad(A[cr], P, 'constant', constant_values=0)[P:-P, x[0]:x[1], y[0]:y[1]]
                else:
                    data = A[cr,:, x[0]:x[1], y[0]:y[1]]
                C = data*W[i[0]]
                feature = np.argmax(np.sum(C, axis=(2,1)))
                layer_out.append((feature, x[0], y[0]))
            X[cr] = list(set(layer_out))
    return X

def discriminative_locations_deconvolution(X, W, A, K, S, P):
    """Calculates outgoing discriminative locations
    inputs
    X: incoming discriminative locations from higher layer
    W: weights of higher layer
    A: activations at current layer
    K: kernel of higher layer
    S: stride of higher layer
    output
    outgoing discriminative locations of current layer
    """

    for cr in range(5):
        layer_out = []
        for i in X[cr]:
            x = (i[1]*S, i[1]*S+K)
            y = (i[2]*S, i[1]*S+K)
            if (P != 0):
                data = np.lib.pad(A[cr], P, 'constant', constant_values=0)[P:-P, x[1]:x[0], y[1]:y[0]]
            else:
                data = A[cr,:, x[1]:x[0], y[1]:y[0]]
            C = data*W[i[0]]
            feature = np.argmax(np.sum(C, axis=(2,1)))
            layer_out.append((feature, x[0], y[0]))
        X[cr] = list(set(layer_out))
    return X


def data(points, inc, resFac):
        output = []
        for cr in range(5):
            if (points[cr] != 0):
                layer_out = []
                # Bringing points back to image size
                for i in points[cr]:
                    layer_out.append([int((i[1]+inc[cr][0])*(1/resFac)),
                                      int((i[2]+inc[cr][1])*(1/resFac))])
                output.extend(layer_out)
        return np.array(output)


def fixations(net, img, offset, resFac):
    p = net.predict(img)
    p_m = np.argmax(np.mean(p, axis=0))
    labels = [np.argmax(p[i]) for i in range(5)]
    points = []
    for i in range(5):
        if np.argmax(p[i, :]) == p_m:
            points.append([int(p_m)])
        else:
            points.append([0])

    points = discriminative_locations_fully_connected(points, net.net.params['fc8'][0].data, net.net.blobs['fc7'].data)
    points = discriminative_locations_fully_connected(points, net.net.params['fc7'][0].data, net.net.blobs['fc6'].data)
    points = discriminative_locations_fully_connected(points, net.net.params['fc6'][0].data, net.net.blobs['pool5'].data)
    points = discriminative_locations_pool(points, net.net.blobs['conv5_3'].data, 2, 2)
    points = discriminative_locations_convolution(points, net.net.params['conv5_3'][0].data, net.net.blobs['conv5_2'].data, 3, 1, 1)
    points = discriminative_locations_convolution(points, net.net.params['conv5_2'][0].data, net.net.blobs['conv5_1'].data, 3, 1, 1)
    points = discriminative_locations_convolution(points, net.net.params['conv5_1'][0].data, net.net.blobs['pool4'].data, 3, 1, 1)
    points = discriminative_locations_pool(points, net.net.blobs['conv4_3'].data, 2, 2)
    points = discriminative_locations_convolution(points, net.net.params['conv4_3'][0].data, net.net.blobs['conv4_2'].data, 3, 1, 1)
    points = discriminative_locations_convolution(points, net.net.params['conv4_2'][0].data, net.net.blobs['conv4_1'].data, 3, 1, 1)
    points = discriminative_locations_convolution(points, net.net.params['conv4_1'][0].data, net.net.blobs['pool3'].data, 3, 1, 1)
    points = discriminative_locations_pool(points, net.net.blobs['conv3_3'].data, 2, 2)
    points = discriminative_locations_convolution(points, net.net.params['conv3_3'][0].data, net.net.blobs['conv3_2'].data, 3, 1, 1)
    points = discriminative_locations_convolution(points, net.net.params['conv3_2'][0].data, net.net.blobs['conv3_1'].data, 3, 1, 1)
    points = discriminative_locations_convolution(points, net.net.params['conv3_1'][0].data, net.net.blobs['pool2'].data, 3, 1, 1)
    points = discriminative_locations_pool(points, net.net.blobs['conv2_2'].data, 2, 2)
    points = discriminative_locations_convolution(points, net.net.params['conv2_2'][0].data, net.net.blobs['conv2_1'].data, 3, 1, 1)
    points = discriminative_locations_convolution(points, net.net.params['conv2_1'][0].data, net.net.blobs['pool1'].data, 3, 1, 1)
    points = discriminative_locations_pool(points, net.net.blobs['conv1_2'].data, 2, 2)
    points = discriminative_locations_convolution(points, net.net.params['conv1_2'][0].data, net.net.blobs['conv1_1'].data, 3, 1, 1)
    points = data(points, offset, resFac)

    points = list(map(lambda x: x*resFac, points))
    return points
