from deep_introspection.lrp import calculate_lrp_heatmap
from deep_introspection.features import extract_features_from_relevances
from deep_introspection.fixations import fixations
from deep_introspection import network, utils, synthesis
import random
import cv2
import scipy.misc
import matplotlib.pyplot as plt
from skimage.feature import hog
import caffe

import numpy as np
import scipy as sp
import scipy.stats
from scipy.misc import imread, imresize

import os
import time
from skimage import transform, io, img_as_float

import itertools

def mean_confidence_interval(data, confidence=0.95):
    a = 1.0*np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * sp.stats.t._ppf((1+confidence)/2., n-1)
    return m, h


def sa(net, img):
    net.predict(img)
    layer = 'prob'
    activations = net.get_activations(layer)

    grad = net.backward(layer, activations)
    return np.mean(np.abs(grad), axis=2)

path = 'deep_introspection\\test\\shape_model\\'
#caffenet = caffe.Net('shapes_test/shapes_net_test.prototxt',caffe.TEST)
net = network.CaffeNet('shapes_test/shapes_net_test.prototxt','shapes_test/weights.caffemodel')
#
# net = network.TensorFlowNet('deep_introspection/test/shape_model/model.ckpt-40000.meta', './deep_introspection/test/shape_model/')
# fc1_weights = net.sess.graph.get_tensor_by_name('fc1/kernel:0').eval(session=net.sess)
# fc1_biases = net.sess.graph.get_tensor_by_name('fc1/bias:0').eval(session=net.sess)
# fc2_weights = net.sess.graph.get_tensor_by_name('fc2/kernel:0').eval(session=net.sess)
# fc2_biases = net.sess.graph.get_tensor_by_name('fc2/bias:0').eval(session=net.sess)
# conv1_weights = net.sess.graph.get_tensor_by_name('conv1/kernel:0').eval(session=net.sess)
# conv1_biases = net.sess.graph.get_tensor_by_name('conv1/bias:0').eval(session=net.sess)
# conv2_weights = net.sess.graph.get_tensor_by_name('conv2/kernel:0').eval(session=net.sess)
#
# conv2_biases = net.sess.graph.get_tensor_by_name('conv2/bias:0').eval(session=net.sess)
# caffenet.params['conv1'][0].data[...] = conv1_weights.T
# caffenet.params['conv1'][1].data[...] = conv1_biases
# caffenet.params['conv2'][0].data[...] = conv2_weights.T
# caffenet.params['conv2'][1].data[...] = conv2_biases
#
# caffenet.params['fc1'][0].data[...] = fc1_weights.T
# caffenet.params['fc1'][1].data[...] = fc1_biases
# caffenet.params['fc2'][0].data[...] = fc2_weights.T
# caffenet.params['fc2'][1].data[...] = fc2_biases

#caffenet.save("shapes_test/weights.caffemodel")

full_path = os.getcwd()+"\\" + path

test_files = []
for _, dirnames, filenames in os.walk(full_path):
    for file in filenames:
        if file.endswith('.jpg'):
            test_files.append(path+file)
print(test_files)
# random.shuffle(test_files)
# correct = 0
# for i in range(2048):
#     filename = test_files[i]
#     img, newSize = utils.shapenetPreprocess(filename)
#     net.set_new_size(newSize)
#     if "quad" in filename:
#         real_answer = 0
#     else:
#         real_answer = 1
#
#     if real_answer == np.argmax(net.predict(img)):
#         correct+=1
# print(correct/2048)

#### Speed Evaluation ####
# times = np.zeros((len(test_files), 4))
# avg = 0
#
# for i in range(len(test_files)):
#     filename = test_files[i]
#     img, newSize = utils.shapenetPreprocess(filename)
#     net.set_new_size(newSize)
#
#     start = time.time()
#     net.predict(img)
#     avg += (time.time()-start)
#
#     start = time.time()
#     sa(net, img)
#     times[i,0] = time.time()-start
#
#     start = time.time()
#     relevances = calculate_lrp_heatmap(net, img)
#     times[i,2] = time.time()-start
#
#     start = time.time()
#     extract_features_from_relevances(relevances)
#     times[i,3] = time.time()-start+times[i,2]
#
#     start = time.time()
#     points = fixations(net, img, [[0,0]])
#     utils.obtain_heatmap(points, img)
#     times[i,1] = (time.time()-start)
#
# avg/=len(test_files)
# # subtract prediction time
# times -= avg
#
# for i in range(times.shape[1]):
#     print(mean_confidence_interval(times[:,i]))

########

#### Accuracy Evaluation ####

# for i in range(len(test_files)):
#
#     filename = test_files[i]
#
#     img, newSize = utils.shapenetPreprocess(img_path=filename)
#     net.set_new_size(newSize)
#     print(filename, net.predict(img))
#
#     sa_result = sa(net, img)
#     relevances = calculate_lrp_heatmap(net, img)
#     points = fixations(net, img, [[0,0]])
#     hm = utils.obtain_heatmap(points, img)[:112,:112]
#     features = np.array(extract_features_from_relevances(np.copy(relevances)))
#     features = list(itertools.chain.from_iterable(features))
#
#     features_map = np.zeros(relevances.shape)
#     for index in features:
#         features_map[tuple(index)] = relevances[tuple(index)]
#
#
#     img += 133.4984
#     img /= 255
#
#     img = img.reshape(img.shape[0],img.shape[1])
#     _, ax = plt.subplots(1, 4, figsize=(20, 5))
#     ax[0].imshow(img), ax[0].axis('off'), ax[0].imshow(sa_result, 'jet', alpha=0.8), ax[0].set_title('Sensitivity Analysis')
#     ax[1].imshow(img), ax[1].axis('off'),  ax[1].imshow(hm, 'jet', alpha=0.5), ax[1].scatter(points[:,1],points[:,0]), ax[1].set_title('CNN Fixations')
#     ax[2].imshow(img), ax[2].axis('off'), ax[2].imshow(relevances, 'jet', alpha=0.8,vmin=0, vmax=1e-3), ax[2].set_title('LRP')
#     ax[3].imshow(img), ax[3].axis('off'), ax[3].imshow(features_map, 'jet', alpha=0.8, vmin=0, vmax=1e-3), ax[3].set_title('Our Method')
#
#     plt.show()

########


#### Synthesis Evaluation ####
# print(np.load("reconstruction_errors.npy"))
# num = 10
# reconstruction_errors = np.zeros(shape=(5, 10))
# for i in range(5):
#     filename = test_files[i]
#     print(filename)
#     img, newSize = utils.shapenetPreprocess(img_path=filename)
#     net.set_new_size(newSize)
#
#     relevances = calculate_lrp_heatmap(net, img)
#
#     features = np.array(extract_features_from_relevances(np.copy(relevances)))
#
#     feature = np.array(random.choice(features))
#     xmax, ymax, xmin, ymin = np.max(feature[:,1]), np.max(feature[:,0]), np.min(feature[:,1]), np.min(feature[:,0])
#
#     layer = net.get_layer_names()[-2]
#     print(layer)
#     for j in range(num):
#         #net.predict(img)
#         feature_img, reconstruction_errors[i,j] = synthesis.synthesise_boundary(net, img, layer, xmax,ymax,xmin,ymin)
#
#         np.save("feature_" + str(i) + "_reconstruction_" + str(j) + ".npy", feature_img)
#         np.save("reconstruction_errors.npy", reconstruction_errors)


reconstruction_errors = np.load("reconstruction_errors.npy")
np.save("reconstruction_errors.npy", reconstruction_errors)
means_per_feature = np.mean(reconstruction_errors, axis = 1)
sds_per_feature = np.std(reconstruction_errors, axis = 1)


print(means_per_feature, sds_per_feature)
print(np.mean(means_per_feature), np.mean(sds_per_feature))
###
im = np.load('36_55_23_28.npy')
im = im.reshape(im.shape[0],im.shape[1])
### Naturalness Evaluation

fd, hog_image = hog(im, orientations=8, pixels_per_cell=(16, 16),
                    cells_per_block=(1, 1), visualise=True)
print(fd)
