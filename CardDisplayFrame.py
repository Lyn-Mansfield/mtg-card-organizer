import tkinter as tk
from PIL import Image
from PIL import ImageTk
import requests
from io import BytesIO


class CardDisplayFrame(tk.Frame):
	image = None
	instances = []
	# Full-size scale is 750 x 1050, this is half that
	ideal_viewing_size = (375, 525)

	def __init__(self, root, **kwargs):
		super().__init__(root, **kwargs)
		# Janky work-around to reserving enough space
		self.pixel = tk.PhotoImage(width=1, height=1)
		self.display_port = tk.Label(
			self, 
			image=self.pixel,
			width=self.ideal_viewing_size[0],
			height=self.ideal_viewing_size[1],
			relief=tk.SUNKEN
		)
		self.display_port.pack()
		self.instances.append(self)

	def display(self):
		self.display_port.configure(image=self.image)

	def clear(self):
		self.display_port.configure(
			image=self.pixel,
			width=self.ideal_viewing_size[0],
			height=self.ideal_viewing_size[1]
		)

	@classmethod
	def display_new_image(cls, image_link):
		response = requests.get(image_link)
		image = Image.open(BytesIO(response.content))

		resized_image = image.resize(cls.ideal_viewing_size)

		cls.image = ImageTk.PhotoImage(resized_image)
		# Broadcast image to all display frames
		for display_frame in cls.instances:
			display_frame.display()

	@classmethod
	def clear_all(cls):
		for display_frame in cls.instances:
			display_frame.clear()