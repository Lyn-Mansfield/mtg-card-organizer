import tkinter as tk
from PIL import Image
from PIL import ImageTk
import requests
from io import BytesIO


class CardDisplayFrame(tk.Frame):
	def __init__(self, root, **kwargs):
		super().__init__(root, **kwargs)
		
		self.image = None
		self.display_port = tk.Label(self, image=None)
		self.display_port.pack()

	def display_image(self, image_link):
		response = requests.get(image_link)
		image = Image.open(BytesIO(response.content))

		# Scale to 750 x 1050
		appropriate_size = (375, 525)
		resized_image = image.resize(appropriate_size)


		self.image = ImageTk.PhotoImage(resized_image)
		self.display_port.configure(image=self.image)

test_link = "https://cards.scryfall.io/png/front/f/b/fb62605c-a58e-4e53-8336-b2bee316b5a6.png?1751992298"

root = tk.Tk()
root.title("Test")

test_label = tk.Label(root, text='bruh!')
test_label.grid(row=0, column=0)

card_display_frame = CardDisplayFrame(root)
card_display_frame.grid(row=1, column=0)
card_display_frame.display_image(test_link)

root.mainloop()