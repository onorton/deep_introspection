from PIL import Image, ImageDraw
import numpy as np
from skimage import util
import os

train = 90
test = 10

size = 500


def random_transform_matrix():

    # define scaling matrix
    scale = np.identity(3)
    x = 3*np.random.rand()+0.1
    y = 3*np.random.rand()+0.1
    scale[0,0] = x
    scale[1,1] = y

    # define translation matrix
    translate = np.identity(3)
    x = size/2*(2*np.random.rand()-1)
    y = size/2*(2*np.random.rand()-1)
    translate[0,2] = x
    translate[1,2] = y

    return np.matmul(translate, scale)

def random_quad_matrix():
    m = random_transform_matrix()
    # define rotation matrix
    rotation = np.identity(3)
    sin = 2*np.random.rand()-1
    cos = 2*np.random.rand()-1
    rotation[0,0] = cos
    rotation[0,1] = -sin
    rotation[1,0] = sin
    rotation[1,1] = cos
    return np.matmul(m, rotation)


def generate_noisy_image():
    im = np.zeros(shape=(size,size,3))
    im = 255*util.random_noise(im, mode='gaussian', mean=0.5)
    im = Image.fromarray(np.uint8(im))
    return im

def generate_quad():
    points = np.array([[200,200,1],[300,200,1],[300,300,1],[200,300,1]])
    points[:,0:2] -= size//2
    points = points.transpose()

    m = random_quad_matrix()
    points = np.matmul(m, points).transpose()
    points[:,0:2] += size//2

    point_list = []
    for p in points:
        point_list.append((p[0]/p[2],p[1]/p[2]))

    im = generate_noisy_image()
    draw = ImageDraw.Draw(im)
    draw.polygon(point_list, fill=(255,255,255))
    return im

def generate_ellipse():
    points = np.array([[425,425,1],[575,575,1]])
    points[:,0:2] -= size
    points = points.transpose()

    m = random_transform_matrix()
    points = np.matmul(m, points).transpose()
    points[:,0:2] += size

    point_list = []
    for p in points:
        point_list.append((p[0]/p[2],p[1]/p[2]))


    im = np.zeros(shape=(2*size,2*size,3))
    im = Image.fromarray(np.uint8(im))
    draw = ImageDraw.Draw(im)
    draw.ellipse(point_list, fill=(255,255,255))
    im = im.rotate(np.random.rand()*360).resize((size, size))
    im = np.array(im)
    bg = np.array(generate_noisy_image()).flatten()
    indices = np.argwhere(im.flatten() > 0)
    bg[indices] = 255
    bg = bg.reshape((size,size,3))
    return Image.fromarray(np.uint8(bg))

if not os.path.exists('data/train/quads'):
  os.makedirs('data/train/quads')

if not os.path.exists('data/test/quads'):
  os.makedirs('data/test/quads')

if not os.path.exists('data/train/ellipses'):
  os.makedirs('data/train/ellipses')

if not os.path.exists('data/test/ellipses'):
  os.makedirs('data/test/ellipses')

for i in range(train):
    quad = generate_quad()
    quad.save('data/train/quads/quad_'+str(i)+'.jpg')
    ellipse = generate_ellipse()
    ellipse.save('data/train/ellipses/ellipse_'+str(i)+'.jpg')

for i in range(test):
    quad = generate_quad()
    quad.save('data/test/quads/quad_'+str(i)+'.jpg')
    ellipse = generate_ellipse()
    ellipse.save('data/test/ellipses/ellipse_'+str(i)+'.jpg')
