from PIL import Image, ImageDraw
import numpy as np
from skimage import util

num = 10

def random_transform_matrix():
    return np.array([[1, 0, 0],[0, 1, 0],[0,0,1]])

def generate_noisy_image():
    im = np.zeros(shape=(500,500,3))
    im = 255*util.random_noise(im, mode='gaussian')
    im = Image.fromarray(np.uint8(im))
    return im

def generate_quad():
    points = np.array([[200,200,1],[300,200,1],[300,300,1],[200,300,1]])
    points[:,0:1] -= 250
    points = points.transpose()

    m = random_transform_matrix()
    points = np.matmul(m, points).transpose()
    points[:,0:1] += 250

    point_list = []
    for p in points:
        point_list.append((p[0]/p[2],p[1]/p[2]))

    im = generate_noisy_image()
    draw = ImageDraw.Draw(im)
    draw.polygon(point_list, fill=(255,255,255))
    return im

def generate_ellipse():
    points = np.array([[200,200,1],[300,300,1]])
    points[:,0:1] -= 250
    points = points.transpose()

    m = random_transform_matrix()
    points = np.matmul(m, points).transpose()
    points[:,0:1] += 250

    point_list = []
    for p in points:
        point_list.append((p[0]/p[2],p[1]/p[2]))
        
    im = generate_noisy_image()
    draw = ImageDraw.Draw(im)
    draw.ellipse(point_list, fill=(255,255,255))
    return im

for i in range(num):
    quad = generate_quad()
    quad.save('data/quads/quad_'+str(i)+'.jpg')

for i in range(num):
    ellipse = generate_ellipse()
    ellipse.save('data/ellipses/ellipse_'+str(i)+'.jpg')
