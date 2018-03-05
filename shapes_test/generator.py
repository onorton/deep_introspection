from PIL import Image, ImageDraw
import numpy as np
from skimage import util
import os

train = 8192
test = 1024

size = 224


def random_quad_matrix():
    # define rotation matrix
    rotation = np.identity(3)
    sin = 2*np.random.rand()-1
    cos = 2*np.random.rand()-1
    rotation[0,0] = cos
    rotation[0,1] = -sin
    rotation[1,0] = sin
    rotation[1,1] = cos

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

    return np.matmul(np.matmul(translate, scale), rotation)

def random_ellipse_matrix():
    # define scaling matrix
    scale = np.identity(3)
    x = 3*np.random.rand()+0.5
    y = 3*np.random.rand()+0.5
    scale[0,0] = x
    scale[1,1] = y

    # define translation matrix
    translate = np.identity(3)
    x = size/3*(2*np.random.rand()-1)
    y = size/3*(2*np.random.rand()-1)
    translate[0,2] = x
    translate[1,2] = y

    return np.matmul(translate, scale)



def generate_noisy_image():
    im = np.zeros(shape=(size,size,3))
    im = 255*util.random_noise(im, mode='gaussian', mean=0.5)
    im = Image.fromarray(np.uint8(im))
    return im
def generate_quad():
    points = np.array([[87,87,1],[87,137,1],[137,137,1],[137,87,1]])
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
    points = np.array([[87,87,1],[137,137,1]])
    points[:,0:2] -= size//2
    points = points.transpose()

    m = random_ellipse_matrix()
    points = np.matmul(m, points).transpose()
    points[:,0:2] += size//2 + 87

    point_list = []
    for p in points:
        point_list.append((p[0]/p[2],p[1]/p[2]))


    im = np.zeros(shape=(size*2,size*2,3))
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

if not os.path.exists('data/test'):
  os.makedirs('data/test')

if not os.path.exists('data/train'):
  os.makedirs('data/train')

for i in range(train):
    quad = generate_quad()
    quad.save('data/train/quad_'+str(i)+'.jpg')
    ellipse = generate_ellipse()
    ellipse.save('data/train/ellipse_'+str(i)+'.jpg')

for i in range(test):
    quad = generate_quad()
    quad.save('data/test/quad_'+str(i)+'.jpg')
    ellipse = generate_ellipse()
    ellipse.save('data/test/ellipse_'+str(i)+'.jpg')
