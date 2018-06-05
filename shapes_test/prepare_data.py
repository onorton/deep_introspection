import numpy as np
import lmdb
import caffe
import os
from PIL import Image
import re
import random

def create_lmdb(set):
    path = os.getcwd()+"\\data\\" + set + "\\"

    number_files = 0
    for _, dirnames, filenames in os.walk(path):
      # ^ this idiom means "we won't be using this value"
        number_files += len(filenames)

    env = lmdb.open('qe_'+set+'_lmdb', map_size=number_files*200000)

    with env.begin(write=True) as txn:
        i = 0
        for root, dirs, files in os.walk(path):
            random.shuffle(files)
            for file in files:
                if file.endswith(".jpg"):

                    im = Image.open(os.path.join(root, file))
                    im = np.array(im)
                    datum = caffe.proto.caffe_pb2.Datum()
                    datum.channels = im.shape[2]
                    datum.height = im.shape[0]
                    datum.width = im.shape[1]
                    datum.data = im.tobytes()

                    str_id = ''
                    if re.search(r'quad_[0-9]+\.jpg', file) :
                        datum.label = 0
                        str_id = 'quad_{:08}'.format(i)
                    else :
                        datum.label = 1
                        str_id = 'ellipse_{:08}'.format(i)
                    i+=1

                    txn.put(str_id.encode('ascii'), datum.SerializeToString())

def create_npy(set):
    path = os.getcwd()+"\\data\\" + set + "\\"

    number_files = 0
    for _, dirnames, filenames in os.walk(path):
        number_files += len(filenames)

    images = np.zeros((number_files,112,112)).astype('float32')
    labels = np.zeros(number_files)


    i = 0
    for root, dirs, files in os.walk(path):
        random.shuffle(files)
        for file in files:
            if file.endswith(".jpg"):
                im = Image.open(os.path.join(root, file))
                im = np.array(im)
                images[i] = im
                if re.search(r'quad_[0-9]+\.jpg', file) :
                    labels[i] = 0
                else :
                    labels[i] = 1
                i+=1
                if i%100 == 0:
                    print(str(i) + ' examples processed.')
    print("Saving images...")
    np.save(set+'_images.npy', images)
    print("Images saved.")
    print("Saving labels...")
    np.save(set+'_labels.npy', labels)
    print("Labels saved.")
create_npy('train')
create_npy('test')
create_lmdb('train')
create_lmdb('test')
