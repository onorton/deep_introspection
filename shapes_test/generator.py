from PIL import Image, ImageDraw

num = 10

def generate_quad():
    points = [(200,200),(300,200),(300,300),(200,300)]
    im = Image.new('RGB', (500, 500), (255, 255, 255))
    draw = ImageDraw.Draw(im)
    for p in range(len(points)):
        draw.line(points[p%len(points)]+points[(p+1)%len(points)], fill=(0,0,0), width=3)
    return im

for i in range(num):
    quad = generate_quad()
    quad.save('data/quads/quad_'+str(i)+'.jpg')
