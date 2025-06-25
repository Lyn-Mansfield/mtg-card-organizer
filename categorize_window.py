import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk
from CardEntryFrame import CardEntryFrame
from CategoryBlockFrame import CategoryBlockFrame
from SidebarFrame import SidebarFrame

class MultiColumnListboxApp:
    def __init__(self, root):
        # Root setup
        self.root = root
        self.root.geometry("800x600")
        self.root.title("MTG Deck Column Organizer")

        # Sidebar frame
        self.sidebar_frame = SidebarFrame(root, highlightbackground='yellow', highlightthickness=4)


        # Body frame
        self.body_frame = tk.Frame(root, highlightbackground='red', highlightthickness=4)
        self.body_frame.pack(side=tk.LEFT, padx=10, pady=10, expand=True, fill=tk.BOTH)

        # Input frame
        self.input_frame = CardEntryFrame(
            self.body_frame, 
            add_item_command=self.add_new_item, 
            add_cat_command=self.add_custom_category, 
            highlightbackground='white', 
            highlightthickness=3
        )
        self.input_frame.pack(side=tk.TOP, fill=tk.X)

        # Block frame
        self.block_frame = CategoryBlockFrame(
            self.body_frame,
            highlightbackground='black', 
            highlightthickness=3
        )
        self.block_frame.pack(padx=10, pady=(0, 10), expand=True, fill=tk.BOTH)

        # Add default categories
        self._add_default_categories()

    def _add_default_categories(self):
        # Initial setup
        default_categories = {
            'u': "Unsorted",
            'c': "Card Draw",
            'p': "Protection",
            't': "Tutor",
            's': "Sac Outlet",
            'm': "Mana Ramp",
            'l': "Land"
        }
        for (keybind, name) in default_categories.items():
            self.add_category(keybind, name)

    def add_category(self, keybind, name):
        # Add category to options menu
        self.input_frame.add_category(keybind=keybind, name=name)

        # Add a new category block
        self.block_frame.add_category(keybind, name)

    def add_custom_category(self, event):
        # Get custom category information
        try:
            (keybind, name) = self.input_frame.output_new_cat_entries()
        except Exception as e:
            return

        self.add_category(keybind, name)
    
    def add_new_item(self, event):
        print("trying to add new item!")
        # Add an item to the selected category
        target_category = self.input_frame.get_curr_category()
        new_item = self.input_frame.output_card_search()

        if new_item is None:
            return
        self.block_frame.add_new_item(new_item, target_category)


root = tk.Tk()
app = MultiColumnListboxApp(root)

root.mainloop()