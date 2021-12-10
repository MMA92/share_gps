import time
import threading
import random
import queue
import win32api, win32con, pywintypes,win32gui
import keyboard
import sys

import tkinter as tk
from PIL import Image, ImageTk

from main import GPSVis
from client import get_gps


alpha = 1.0
fullscreen = False


def pressed_keys(e):
	global alpha,fullscreen
	if e.name == "f2":
		if alpha == 1.0:
			alpha = 0.0
		else:
			alpha = 1.0
		print("f2 pressed")
	if e.name == "f3":
		fullscreen = not fullscreen
		print("f3 pressed")


class GuiPart:
	def __init__(self, master, queue, endCommand):
		self.queue = queue

	def processIncoming(self):
		"""
		Handle all the messages currently in the queue (if any).
		"""
		global alpha

		while self.queue.qsize():
			
			try:
				q = self.queue.get()

				root.wm_attributes("-transparentcolor", "white")
				root.wm_attributes('-alpha', alpha)				
				print(time.strftime("%H:%M:%S"))

			except queue.Empty:					
				pass

class ThreadedClient:	
	def __init__(self, root,label):
		
		self.root = root
		self.label = label
		self.queue = queue.Queue() 	# Create the queue
		self.photo = None
		self.size = (333,192)

		self.gui = GuiPart(root, self.queue, self.endApplication) # Set up the GUI part

		self.running = 1
		self.thread1 = threading.Thread(target=self.workerThread1)
		self.thread1.start()
		self.periodicCall() # Start the periodic call in the GUI to check if the queue contains	# anything

	def update_text(self,data):		
		
		v = data["verticalAccuracy"]
		a = int(data["altitude"]) - 48  #local offset for baden-württemberg
		alitude = f"{a}m ±{v}m"

		accuracy = str(round(float(data["accuracy"]),2))

		text_boxes[0]["text"] = data["counter"]
		text_boxes[1]["text"] = data["lati"]
		text_boxes[2]["text"] = data["long"]
		text_boxes[3]["text"] = "sats: " + data["satellites"]
		text_boxes[4]["text"] = data["method"]
		text_boxes[5]["text"] = "± " + accuracy
		text_boxes[6]["text"] = alitude
		text_boxes[7]["text"] = data["speed"] + "km/h"
		
	def periodicCall(self):
		"""
		Check every 100 ms if there is something new in the queue.
		"""

		data = get_gps()
		#data_points = [[random.uniform(48.7,49.0),random.uniform(8.1,9.6) ]]
		if data != None:
			data_points = [[float(data["lati"]),float(data["long"])]]
			self.update_text(data)		
			img = vis.create_image(color=(255, 0, 0), width=3)
			img = vis.draw_points(img,data=data_points)
			img = img.resize(self.size, Image.ANTIALIAS)
		
			self.photo = ImageTk.PhotoImage(img,master=self.root)
			self.label.config(image = self.photo) 

		if fullscreen:
			self.root.geometry("1400x1000+22+44")
			self.size = (round(333*3.85),round(192*3.85))
		else:
			self.root.geometry("400x400+30+30")
			self.size = (333,192)


		self.gui.processIncoming()
		if not self.running:			
			sys.exit(1)
		self.root.after(500, self.periodicCall)

	def workerThread1(self):	
		while self.running:			
			self.queue.put("")
			time.sleep(0.5)

	def endApplication(self):
		self.running = 0



data_points = [[49.0069, 8.4037],
[48.78558610988896, 9.196924677082437],
[48.7132, 9.4197],
[48.70807018950797, 9.380981119843291]]

gps = get_gps()
#x,y = float(gps["long"]),float(gps["lati"])
#print("data from gps",x,y)
#data_points = [[y,x]]
data_points = [[48.8922, 8.6946]] #pforzheim


c = [8.16496741498219,48.6428830564991,9.67047534022183,49.0708984229151] #bords of map

min_x,max_x = c[0],c[2]
min_y,max_y = c[1],c[3]


vis = GPSVis(data=data_points,
        map_path='data/bw.png',  # Path to map downloaded from the OSM.
        points=(max_y, min_x, min_y, max_x)) # Two coordinates of the map (upper left, lower right)

img = vis.create_image(color=(255, 0, 0), width=3)  # Set the color and the width of the GNSS tracks.
img = vis.draw_points(img)  
img = img.resize((333,192), Image.ANTIALIAS) #333,192



root = tk.Tk()

root.geometry("400x400+30+30") # empty
root.configure(background='white')

frame = tk.Frame(width = 400 ,height=400, bg="white") #red
frame.place(x=0,y=0)

ph = ImageTk.PhotoImage(img,master=root)


root.overrideredirect(True)
root.lift()
root.wm_attributes("-topmost", True)
root.wm_attributes("-disabled", True)
root.wm_attributes("-transparentcolor", "white")
root.deiconify()

panel = tk.Label(frame, image = ph,background="white")
panel.pack(side = "bottom", fill = "both", expand = "yes")

posis = [(0,210),(0,240),(0,270),(0,300),
(180,210),(180,240),(180,300),(180,300)]
text_boxes = []
for i in range(8):
	label = tk.Label(root,text = "NaN", font =("Courier", 14),fg="#888888")
	label.place(x=posis[i][0],y=posis[i][1])
	text_boxes.append(label)


##make window unclickable
hWindow = pywintypes.HANDLE(int(frame.master.frame(), 16))
exStyle = win32con.WS_EX_COMPOSITED | win32con.WS_EX_LAYERED | win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TOPMOST | win32con.WS_EX_TRANSPARENT
win32api.SetWindowLong(hWindow, win32con.GWL_EXSTYLE, exStyle)
##end make window unclickable


keyboard.on_press(pressed_keys)
client = ThreadedClient(root,panel)
root.mainloop()