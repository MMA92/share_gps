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

def pressed_keys(e):
	global alpha
	if e.name == "f2":
		if alpha == 1.0:
			alpha = 0.0
		else:
			alpha = 1.0
		print("f2 pressed")


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

		w1["text"] = data["counter"]
		w2["text"] = data["lati"]
		w3["text"] = data["long"]
		w4["text"] = "sats: " + data["satellites"]
		w5["text"] = data["method"]
		w6["text"] = "± " + accuracy
		w7["text"] = alitude
		w8["text"] = data["speed"] + "km/h"
		
	def periodicCall(self):
		"""
		Check every 100 ms if there is something new in the queue.
		"""

		data = get_gps()
		#data_points = [[random.uniform(48.7,49.0),random.uniform(8.1,9.6) ]]
		data_points = [[float(data["lati"]),float(data["long"])]]

		self.update_text(data)		

		img = vis.create_image(color=(255, 0, 0), width=3)
		img = vis.draw_points(img,data=data_points)
		img = img.resize((333,192), Image.ANTIALIAS)
		self.photo = ImageTk.PhotoImage(img,master=self.root)
		self.label.config(image = self.photo) 

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


w1 = tk.Label(root,text = "NaN", font =("Courier", 14),fg="#888888")
w2 = tk.Label(root,text = "NaN", font =("Courier", 14),fg="#888888")
w3 = tk.Label(root,text = "NaN", font =("Courier", 14),fg="#888888")
w4 = tk.Label(root,text = "NaN", font =("Courier", 14),fg="#888888")
w5 = tk.Label(root,text = "NaN", font =("Courier", 14),fg="#888888")
w6 = tk.Label(root,text = "NaN", font =("Courier", 14),fg="#888888")
w7 = tk.Label(root,text = "NaN", font =("Courier", 14),fg="#888888")
w8 = tk.Label(root,text = "NaN", font =("Courier", 14),fg="#888888")
w1.place(x=0,y=210)
w2.place(x=0,y=240)
w3.place(x=0,y=270)
w4.place(x=0,y=300)
w5.place(x=180,y=210)
w6.place(x=180,y=240)
w7.place(x=180,y=270)
w8.place(x=180,y=300)


##make window unclickable
hWindow = pywintypes.HANDLE(int(frame.master.frame(), 16))
exStyle = win32con.WS_EX_COMPOSITED | win32con.WS_EX_LAYERED | win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TOPMOST | win32con.WS_EX_TRANSPARENT
win32api.SetWindowLong(hWindow, win32con.GWL_EXSTYLE, exStyle)
##end make window unclickable


keyboard.on_press(pressed_keys)
client = ThreadedClient(root,panel)
root.mainloop()