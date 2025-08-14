import tkinter as tk
from PIL import Image
from PIL import ImageTk
import requests
from io import BytesIO


class CardDisplayFrame(tk.Frame):
	image = None
	image_info_series = None
	current_side = 'N/A'
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

		self.flip_button = tk.Button(self, text="Flip (↻)", command=self.flip)
		self.flip_button.pack()

	def display(self):
		self.display_port.configure(image=self.image)

	def clear(self):
		self.display_port.configure(
			image=self.pixel,
			width=self.ideal_viewing_size[0],
			height=self.ideal_viewing_size[1]
		)

	@classmethod
	def clear_all(cls):
		for display_frame in cls.instances:
			display_frame.clear()
		cls.image = None

	@classmethod
	def _get_image(cls, image_link):
		response = requests.get(image_link)
		image = Image.open(BytesIO(response.content))
		resized_image = image.resize(cls.ideal_viewing_size)

		return ImageTk.PhotoImage(resized_image)

	# Broadcast image to all display frames
	@classmethod
	def _broadcast(cls):
		for display_frame in cls.instances:
			display_frame.display()

	# Takes in a row series and displays the front side of the card
	@classmethod
	def display_new_image(cls, card_row_series):
		cls.image_info_series = card_row_series
		# If there's nothing to display, then display nothing
		if cls.image_info_series is None:
			print('no row selected!')
			CardDisplayFrame.clear_all()
			return

		# If it's a double-sided card, find front-side info and activate flip button 
		if cls.image_info_series['flips'] == True:
			cls.current_side = 'Front'
			front_side_info_df = cls.image_info_series['first_card_info']
			image_link = front_side_info_df['image_uris.png'].item()
		# Otherwise, image link is stored normally
		else:
			cls.current_side = 'N/A'
			image_link = cls.image_info_series['image_uris.png']

		print('getting image!')
		print(card_row_series['first_card_info'])
		print(image_link)
		cls.image = cls._get_image(image_link)
		print('broadcasting!')
		cls._broadcast()
		print('finished broadcasting')

	@classmethod
	def flip(cls):
		match cls.current_side:
			case 'N/A':
				return
			case 'Front':
				cls.current_side = 'Back'
				back_side_info_df = cls.image_info_series['second_card_info']
				image_link = back_side_info_df['image_uris.png'].item()
			case 'Back':
				cls.current_side = 'Front'
				front_side_info_df = cls.image_info_series['first_card_info']
				image_link = front_side_info_df['image_uris.png'].item()

		cls.image = cls._get_image(image_link)
		cls._broadcast()