import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw

from client import get_gps



class GPSVis(object):
    """
        Class for GPS data visualization using pre-downloaded OSM map in image format.
    """
    def __init__(self, data, map_path, points):
        """
        :param data_path: Path to file containing GPS records.
        :param map_path: Path to pre-downloaded OSM map in image format.
        :param points: Upper-left, and lower-right GPS points of the map (lat1, lon1, lat2, lon2).
        """
        self.data = data
        self.points = points
        self.map_path = map_path

        self.result_image = Image
        self.x_ticks = []
        self.y_ticks = []

    def plot_map(self, output='save', save_as='resultMap.png'):
        """
        Method for plotting the map. You can choose to save it in file or to plot it.
        :param output: Type 'plot' to show the map or 'save' to save it.
        :param save_as: Name and type of the resulting image.
        :return:
        """
        self.get_ticks()
        fig, axis1 = plt.subplots(figsize=(10,6))
        axis1.imshow(self.result_image)
        axis1.set_xlabel('Longitude')
        axis1.set_ylabel('Latitude')
        axis1.set_xticklabels(self.x_ticks)
        axis1.set_yticklabels(self.y_ticks)
        #axis1.grid()
        if output == 'save':
            plt.savefig(save_as)
        else:
            plt.show()
        return plt

    def create_image(self, color, width=2):
        """
        Create the image that contains the original map and the GPS records.
        :param color: Color of the GPS records.
        :param width: Width of the drawn GPS records.
        :return:
        """
        
        self.result_image = Image.open(self.map_path, 'r')
        img_points = []
        
        """
        for a in self.data:
            x1, y1 = self.scale_to_img(a, (self.result_image.size[0], self.result_image.size[1]))
            img_points.append((x1, y1))
        """
    
        #draw = ImageDraw.Draw(self.result_image)        
        #draw.line(img_points, fill=color, width=width)

        return self.result_image
    
    def draw_points(self,img, data = None):

        radius = 10
                
        elispe_points = []
        if data == None:
            data = self.data

        for a in data:
            x1, y1 = self.scale_to_img(a, (img.size[0], img.size[1]))
            elispe_points.append((x1-radius,y1-radius,x1+radius,y1+radius))        

        draw = ImageDraw.Draw(img)
        for e in elispe_points:
            draw.ellipse(e, fill=(255,0,0), outline=None, width=100)        

        return img

    def scale_to_img(self, lat_lon, h_w):
        """
        Conversion from latitude and longitude to the image pixels.
        It is used for drawing the GPS records on the map image.
        :param lat_lon: GPS record to draw (lat1, lon1).
        :param h_w: Size of the map image (w, h).
        :return: Tuple containing x and y coordinates to draw on map image.
        """
        # https://gamedev.stackexchange.com/questions/33441/how-to-convert-a-number-from-one-min-max-set-to-another-min-max-set/33445
        old = (self.points[2], self.points[0])
        new = (0, h_w[1])
        y = ((lat_lon[0] - old[0]) * (new[1] - new[0]) / (old[1] - old[0])) + new[0]
        old = (self.points[1], self.points[3])
        new = (0, h_w[0])
        x = ((lat_lon[1] - old[0]) * (new[1] - new[0]) / (old[1] - old[0])) + new[0]
        # y must be reversed because the orientation of the image in the matplotlib.
        # image - (0, 0) in upper left corner; coordinate system - (0, 0) in lower left corner
        return int(x), h_w[1] - int(y)

    def get_ticks(self):
        """
        Generates custom ticks based on the GPS coordinates of the map for the matplotlib output.
        :return:
        """
        self.x_ticks = map(
            lambda x: round(x, 4),
            np.linspace(self.points[1], self.points[3], num=7))
        y_ticks = map(
            lambda x: round(x, 4),
            np.linspace(self.points[2], self.points[0], num=8))
        # Ticks must be reversed because the orientation of the image in the matplotlib.
        # image - (0, 0) in upper left corner; coordinate system - (0, 0) in lower left corner
        self.y_ticks = sorted(y_ticks, reverse=True)



if __name__ == "__main__":
    data_points = [[49.0069, 8.4037],
    [48.78558610988896, 9.196924677082437],
    [48.7132, 9.4197],
    [48.70807018950797, 9.380981119843291]]

    gps = get_gps()
    x,y = float(gps["long"]),float(gps["lati"])
    print("data from gps",x,y)
    data_points = [[y,x]]
    data_points.append([48.8922, 8.6946]) #pforzheim

    c = [8.16496741498219,48.6428830564991,9.67047534022183,49.0708984229151] #bords of map

    min_x,max_x = c[0],c[2]
    min_y,max_y = c[1],c[3]

    vis = GPSVis(data=data_points,
                map_path='data/bw.png',  # Path to map downloaded from the OSM.
                points=(max_y, min_x, min_y, max_x)) # Two coordinates of the map (upper left, lower right)

    vis.create_image(color=(255, 0, 0), width=3)  # Set the color and the width of the GNSS tracks.
    plt = vis.plot_map(output='save')
    plt.show()

    print("done loading map")
