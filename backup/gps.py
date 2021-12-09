import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from mpl_toolkits.axes_grid1 import ImageGrid
from pathlib import Path
import cv2
import numpy as np
from PIL import Image


def join(tiles):

    coords = []
    for k in tiles.keys():
        k = k.split("_")
        x,y = int(k[0]),int(k[1])
        coords.append([x,y])

    min_x = min([x[0] for x in coords])
    min_y = min([x[1] for x in coords])

    nr_y = [x[0] for x in coords].count(min_x)
    nr_x = [x[1] for x in coords].count(min_y)

    i = 256
  
    im = Image.new('RGB', (i*nr_x,i*nr_y), None)    
    # "tiles/{z}/{x}/{y}.png"
    
    for k,v in tiles.items():
        k = k.split("_")
        x,y = int(k[0]),int(k[1])
        y -= min_y
        x -= min_x
        im.paste(v,(x*i, y*i, (x+1)*i, (y+1)*i))

    return im

def load_tiles(zoom = "8"):
    pics = {}
    paths = Path(zoom).iterdir()
    for folder in paths:
        for file in folder.iterdir():
            img = Image.open(str(file))
            pics[folder.stem + "_" + file.stem] = img
    return pics

def coords_to_plot_points(point):

    """point is a list [x,y]"""

    min_x,max_x = 7.7938460065825428,10.064795691466173   
    min_y,max_y = 48.601219958605689,49.245982373309396

    if point[0] > max_x or point[0] < min_x:
        raise ValueError

    if point[1] > max_y or point[1] < min_y:
        raise ValueError



    delta_x = max_x - min_x
    delta_y = max_y - min_y

    pixel_x = delta_x / 768  
    pixel_y = delta_y / 512

    point[0] = point[0] - min_x
    point[1] = point[1] - min_y

    pixel_x = point[0] / pixel_x
    pixel_y = point[1] /pixel_y
    
    
    pixel_x,pixel_y = abs(pixel_x),abs(pixel_y)
    pixel_x,pixel_y = round(pixel_x),round(pixel_y)

    #pixel_x = 768 - pixel_x
    #pixel_y = 512 - pixel_y


    return pixel_x, pixel_y

  



tiles = load_tiles()
new_image = join(tiles)

new_image.save("file.png")



augsburg = [48.3705, 10.8978] #710,410
stuttgart = [48.7758, 9.1829] #388,298
karlsruhe = [49.0069, 8.4037] #252,235


point = stuttgart
point = point[::-1]

print("point",point)

x,y = coords_to_plot_points(point)
print(x,y)


    
#img = mpimg.imread('your_image.png')
imgplot = plt.imshow(new_image)
plt.plot(x,y, 'rp', markersize=14)
#plt.show()





