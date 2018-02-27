from PIL import Image, ImageDraw
import numpy as np
from skimage import util

num = 10

def generate_noisy_image():
    im = np.zeros(shape=(500,500,3))
    im = 255*util.random_noise(im, mode='gaussian')
    im = Image.fromarray(np.uint8(im))
    return im


def generate_quad():
    points = np.array([[200,200],[300,200],[300,300],[200,300]])

    point_list = []
    for p in points:
        point_list.append((p[0],p[1]))

    im = generate_noisy_image()
    draw = ImageDraw.Draw(im)
    draw.polygon(point_list, fill=(255,255,255))
    return im

for i in range(num):
    quad = generate_quad()
    quad.save('data/quads/quad_'+str(i)+'.jpg')
