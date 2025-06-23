import numpy as np
import pandas as pd
from tkinter import *
import os

root = Tk()
root.title("Baby's first app!")

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=0)
root.rowconfigure(1, weight=1)

window_label = Label(root, text="Let's add colors!")
window_label.grid(row=0, column=0, columnspan=2, sticky='ew')

content_frame = Frame(root)
content_frame.grid(row=1, column=0, columnspan=2, sticky='nsew')

# Color listbox stuff start

lst_frame = Frame(content_frame)
lst_frame.grid(row=0, column=0, sticky='nesw')
lst_frame.columnconfigure(0, weight=1)

color_lstbox = Listbox(lst_frame,relief="flat")
color_lstbox.pack(side=LEFT, fill=BOTH, expand=True)

color_lst_scrollbar = Scrollbar(lst_frame, orient=VERTICAL, command=color_lstbox.yview)
color_lst_scrollbar.pack(side=RIGHT, fill=Y)
color_lstbox.configure(yscrollcommand=color_lst_scrollbar.set)

# Color listbox stuff end


# Color option buttons stuff start

color_options_frame = Frame(content_frame, cursor='hand2')
color_options_frame.grid(row=0, column=1, sticky='nesw')

button_container = Frame(color_options_frame)
button_container.pack(expand=True, pady=20)  # Centered with some padding

def add_color(color):
	color_lstbox.insert(END, color)
	items = sorted(color_lstbox.get(0, END))
	color_lstbox.delete(0, END)
	color_lstbox.insert(END, *items)

mtg_colors = sorted(['Black', 'Blue', 'Green', 'White', 'Red'])
for index, color in enumerate(mtg_colors):
	x = Button(button_container, text=color, command=lambda c=color: add_color(c))
	x.grid(row=index, column=1, sticky='ew')

# Color option buttons stuff end

content_frame.rowconfigure(0, weight=1)
content_frame.columnconfigure(0, weight=1)  # List frame expands horizontally
content_frame.columnconfigure(1, weight=0)  # Color options doesn't expand horizontally

root.mainloop()