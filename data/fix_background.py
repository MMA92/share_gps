from PIL import Image
import numpy as np



img = Image.open("data/bw.png")
image_array = np.array(img)


max_value = 220

for i,row in enumerate(image_array):
    for j,pixel in enumerate(row):
        r,g,b = pixel[0:3]
        if r > max_value and g > max_value and b > max_value:
            pixel[0] = max_value
            pixel[1] = max_value
            pixel[2] = max_value

    

x = Image.fromarray(image_array)
x.save("data/bw2.png")
print("done generating image")