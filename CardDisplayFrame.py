import tkinter as tk
from PIL import Image
import requests
from io import BytesIO
from CardImageManager import CardImageManager


class CardDisplayFrame(tk.Frame):
	current_card = None
	image = None
	current_side = 'N/A'
	instances = []

	def __init__(self, root, **kwargs):
		super().__init__(root, **kwargs)
		# Janky work-around to reserving enough space
		self.pixel = tk.PhotoImage(width=1, height=1)
		self.display_port = tk.Label(
			self, 
			image=self.pixel,
			width=CardImageManager.IDEAL_VIEWING_SIZE[0],
			height=CardImageManager.IDEAL_VIEWING_SIZE[1],
			relief=tk.SUNKEN
		)
		self.display_port.pack()
		self.instances.append(self)

		self.flip_button = tk.Button(self, text="Flip (↻)", command=self.attempt_flip)
		self.flip_button.pack()

	def display(self):
		self.display_port.configure(image=self.image)

	def apologize(self):
		self.display_port.configure(text='Still Loading! Check Back Soon xc')

	def clear(self):
		self.display_port.configure(
			image=self.pixel,
			width=CardImageManager.IDEAL_VIEWING_SIZE[0],
			height=CardImageManager.IDEAL_VIEWING_SIZE[1]
		)

	@classmethod
	def clear_all(cls):
		for display_frame in cls.instances:
			display_frame.clear()
		cls.image = None
		cls.current_side = 'N/A'

	# Broadcast image to all display frames
	@classmethod
	def _broadcast(cls):
		for display_frame in cls.instances:
			display_frame.display()

	# Takes in a row series and displays the front side of the card
	@classmethod
	def display_new_image(cls, card_row_series):
		card_name = card_row_series.name
		cls.current_card = card_name
		# If no card is given to display, then clear all
		if card_name is None:
			print('no row selected!')
			CardDisplayFrame.clear_all()
			return

		# If we're still waiting on a card, apologize and move on
		if not CardImageManager.has_images_loaded(card_name):
			print('uh oh! image not loaded yet...')
			cls.clear_all()
			for display_frame in cls.instances:
				display_frame.apologize()
			return
		# Otherwise, get image from CardImageManager
		print(card_row_series['name'], card_row_series['flips'])
		cls.image = CardImageManager.get_image(cls.current_card, 'front')
		cls.current_side = 'Front'
		print('broadcasting!')
		cls._broadcast()
		print('finished broadcasting')

	@classmethod
	def attempt_flip(cls):
		match cls.current_side:
			case 'N/A':
				return
			case 'Front':
				back_image = CardImageManager.get_image(cls.current_card, 'back')
				if back_image is None:
					return
				cls.image = back_image
				cls.current_side = 'Back'
			case 'Back':
				front_image = CardImageManager.get_image(cls.current_card, 'front')
				if front_image is None:
					return
				cls.image = front_image
				cls.current_side = 'Front'

		cls._broadcast()