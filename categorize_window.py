import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from CardEntryFrame import CardEntryFrame
from CategoryBlockFrame import CategoryBlockFrame
from SidebarFrame import SidebarFrame
from UpdateLabel import UpdateLabel
from CardCatManager import CardCatManager
from CardDisplayFrame import CardDisplayFrame
import SavePickler

class MultiColumnListboxApp:
	def __init__(self, root):
		# Root setup
		self.root = root
		self.root.geometry("1080x800")
		self.root.title("MTG Deck Column Organizer")
		self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
		# Fixes tabs not loading when switching between them
		self.root.bind("<Button-1>", lambda x: self.notebook.update_idletasks())

		self.notebook = ttk.Notebook(root)
		self.notebook.pack()

		self.tab_1 = ttk.Frame(self.notebook)
		self.notebook.add(self.tab_1, text='tab_1')

		self.tab_2 = ttk.Frame(self.notebook)
		self.notebook.add(self.tab_2, text='tab_2')
		self.tab_2_label = ttk.Label(self.tab_2, text='Welcome to Tab 2! :D')
		self.tab_2_label.pack()

		# Load any saved info from previous sessions
		SavePickler.load_user_settings()
		SavePickler.load_db_info()

		self.side_frame = tk.Frame(self.tab_1) # , highlightbackground='yellow', highlightthickness=1
		self.side_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)

		# Card display frame
		self.card_display_frame = CardDisplayFrame(self.side_frame)
		self.card_display_frame.pack(side=tk.TOP)

		# Sidebar frame
		self.sidebar_frame = SidebarFrame(self.side_frame)
		self.sidebar_frame.pack(side=tk.TOP, padx=10, pady=10, fill=tk.Y)

		# Body frame
		self.body_frame = tk.Frame(self.tab_1, highlightbackground='red', highlightthickness=4)
		self.body_frame.pack(side=tk.LEFT, padx=10, pady=10, expand=True, fill=tk.BOTH)

		# Header frame
		self.header_frame = tk.Frame(self.body_frame, highlightbackground='purple', highlightthickness=4)
		self.header_frame.pack(side=tk.TOP, fill=tk.X)

		# Update label
		self.update_label = UpdateLabel(self.header_frame)
		self.update_label.pack(side=tk.BOTTOM, fill=tk.X)

		# Input frame
		self.input_frame = CardEntryFrame(
			self.header_frame, 
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

		# Add default categories if no categories already loaded
		if CardCatManager.categories_df.shape[0] == 0:
			self._add_default_categories()
		# Scrub update label after
		UpdateLabel.clear()

		print(CardCatManager.primary_only, CardCatManager.cat_order, CardCatManager.block_order)
#----------------------------------------------------------------------------------------------------#
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
			CardCatManager.add_category(keybind, name)
#----------------------------------------------------------------------------------------------------#	
	def on_closing(self):
		if messagebox.askokcancel("Quit", "Progress will be saved automatically."):
			# Destroy all blocks, since pickle can't save the tkinter blocks in categories df
			CardCatManager.destroy_all_blocks()

			SavePickler.save_user_settings() 
			SavePickler.save_db_info()
			self.root.destroy()


root = tk.Tk()
app = MultiColumnListboxApp(root)

root.mainloop()