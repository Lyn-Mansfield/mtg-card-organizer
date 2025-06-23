import numpy as np
import pandas as pd
from tkinter import *

DEFAULT_MIN_HEIGHT = 3

def add_item(listbox):
    new_item = entry.get()
    if new_item:  # Only add if there's actual text
        listbox.insert(END, new_item)
        entry.delete(0, END)  # Clear the entry field
        
        # Optional: Auto-scroll to the new item
        new_height = max(DEFAULT_MIN_HEIGHT, listbox.size())
        listbox.config(height=new_height)

root = Tk()
root.title("Expandable Listbox Example")

# Frame for the entry and button
input_frame = Frame(root)
input_frame.pack(padx=10, pady=5, fill=X)

# Entry widget
entry = Entry(input_frame)
entry.pack(side=LEFT, expand=True, fill=X, padx=(0, 5))

# Add button
add_button = Button(input_frame, text="Add", command=add_item)
add_button.pack(side=LEFT)

# Listbox with scrollbar
list_frame = Frame(root)
list_frame.pack(padx=10, pady=(0, 10), expand=True, fill=BOTH)

top_listbox = Listbox(
    list_frame,
    height=DEFAULT_MIN_HEIGHT  # Initial height in lines
)
top_listbox.pack(expand=True, fill=BOTH)

bottom_listbox = Listbox(
    list_frame,
    height=DEFAULT_MIN_HEIGHT  # Initial height in lines
)
bottom_listbox.pack(expand=True, fill=BOTH)

# Bind Enter key to also add items
entry.bind('<Return>', lambda event: add_item(top_listbox))
entry.bind('<Command-Return>', lambda event: add_item(bottom_listbox))

root.mainloop()