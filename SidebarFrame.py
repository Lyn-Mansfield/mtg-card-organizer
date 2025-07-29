import tkinter as tk
from tkinter import ttk
from CardCatManager import CardCatManager
import SetParsing
from UpdateLabel import UpdateLabel

class SidebarFrame(tk.Frame):
	def __init__(self, root, **kwargs):
		# Everything lives in self
		super().__init__(root, **kwargs)
		
		# Centered frame, since we want everything in the middle
		self.centered_frame = tk.Frame(self)
		self.centered_frame.pack(expand=True)

		self.buttons_frame = tk.Frame(self.centered_frame)
		self.buttons_frame.pack()
		
		self.import_button = tk.Button(
			self.buttons_frame, 
			text="Import (.txt)", 
			command=SetParsing.import_deck
		)
		self.import_button.pack(side=tk.LEFT)

		self.export_button = tk.Button(
			self.buttons_frame, 
			text="Export (.txt)", 
			command=SetParsing.export_deck
		)
		self.export_button.pack(side=tk.LEFT)

		self.sort_options_title_label = tk.Label(
			self.centered_frame, 
			text='Sort Options',
			font=('Arial', 16, 'underline')
		)

		# All listener variables are instantiated here to be used further down
		self.primary_only_bool_var = tk.BooleanVar(value=CardCatManager.primary_only)
		self.cat_order_string_var = tk.StringVar(value=CardCatManager.cat_order)
		self.block_order_string_var = tk.StringVar(value=CardCatManager.block_order)

		self.primary_only_bool_var.trace_add('write', self._update_class_vars)
		self.cat_order_string_var.trace_add('write', self._update_class_vars)
		self.block_order_string_var.trace_add('write', self._update_class_vars)

		self.primary_only_checkbutton = tk.Checkbutton(
			self.centered_frame, 
			text="Show in primary category only (*)", 
			variable=self.primary_only_bool_var
		)
		self.primary_only_checkbutton.pack(side=tk.TOP)
		if CardCatManager.primary_only:
			self.primary_only_checkbutton.select()

		self.sort_options_title_label.pack(side=tk.TOP, padx=5, pady=5)
		
		self.cat_sort_label = tk.Label(
			self.centered_frame,
			text='Category Sort:'
		)
		self.cat_sort_label.pack(side=tk.TOP, padx=5, pady=5)

		options_menu_width = 9
		# WIP: Add way of broadcasting to CardCatManager whenever a new option is chosen
		cat_sort_options = ['Date Added', 'Alphabetical', 'Size', 'Type', 'Color']
		self.cat_order_options_menu = ttk.OptionMenu(
			self.centered_frame, 
			self.cat_order_string_var, 
			CardCatManager.cat_order, 
			*cat_sort_options
		)
		self.cat_order_options_menu.pack(side=tk.TOP)
		self.cat_order_options_menu.config(width=options_menu_width)

		self.block_sort_label = tk.Label(
			self.centered_frame,
			text='Block Sort:'
		)
		self.block_sort_label.pack(side=tk.TOP, padx=5, pady=5)

		block_sort_options = ['Alphabetical', 'Mana Cost', 'Date Added', 'Number', 'Power', 'Toughness']
		self.block_order_options_menu = ttk.OptionMenu(
			self.centered_frame, 
			self.block_order_string_var, 
			CardCatManager.block_order, 
			*block_sort_options
		)
		self.block_order_options_menu.pack(side=tk.TOP)
		self.block_order_options_menu.config(width=options_menu_width)

		self.test_button = tk.Button(
			self.centered_frame, 
			text="categories test", 
			command=lambda: print([cat_block.name for cat_block in CardCatManager.cat_blocks])
		)
		self.test_button.pack()

	# Update card DB when variables change
	# Random trace_add info gets passed in, too, but we can ignore all that
	def _update_class_vars(self, *args):
		primary_only = self.primary_only_bool_var.get()
		cat_order = self.cat_order_string_var.get()
		block_order = self.block_order_string_var.get()

		CardCatManager._update_class_vars(primary_only, cat_order, block_order)
