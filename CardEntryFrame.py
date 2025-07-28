import pandas as pd
import tkinter as tk
import numpy as np
import time
from tkinter import ttk
import requests
from CardCatManager import CardCatManager
from UpdateLabel import UpdateLabel
import SetParsing

class CardEntryFrame(tk.Frame):
	def __init__(self, root, **kwargs):
		# Everything lives in self
		super().__init__(root, **kwargs)
		# Register self with CardCatManager
		CardCatManager.card_entry_frame = self

		# Card entry
		self.card_entry = ttk.Entry(self)
		self.card_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
		self.card_entry.bind('<Return>', lambda event: self.add_new_item())

		# Category Selection Menu
		self.target_category = tk.StringVar(value="Unsorted")
		self.category_menu = ttk.OptionMenu(
			self, self.target_category, command=lambda _: self.card_entry.focus()
		)
		self.category_menu.pack(side=tk.LEFT, padx=(0, 5))

		# Custom category frame
		self.add_cat_frame = tk.Frame(
			self, 
			highlightbackground='silver', 
			highlightthickness=2
		)
		self.add_cat_frame.pack(side=tk.LEFT, fill=tk.X)

		# Custom category entry
		one_char_validation = (self.register(self._validate_one_char), '%P')
		self.keybind_entry = tk.Entry(
			self.add_cat_frame, 
			width=1,
			validate="key", 
			validatecommand=one_char_validation
		)
		self.keybind_entry.pack(side=tk.LEFT)

		self.cat_name_entry = tk.Entry(self.add_cat_frame)
		self.cat_name_entry.pack(side=tk.LEFT)
		self.cat_name_entry.bind('<Return>', lambda event: self.add_custom_category())

		# Add button
		self.add_button = ttk.Button(
			self.add_cat_frame, text="Add", command=self.add_new_item
		)
		self.add_button.pack(side=tk.LEFT)
#----------------------------------------------------------------------------------------------------#
	def _validate_one_char(self, P):
		if len(P) <= 1:
			return True
		else:
			return False
#----------------------------------------------------------------------------------------------------#
	def get_curr_category(self):
		return self.target_category.get()
#----------------------------------------------------------------------------------------------------#
	def _output_card_search(self):
		original_query = self.card_entry.get()
		self.card_entry.delete(0, tk.END)
		if len(original_query) == 0:
			UpdateLabel.report('Empty query :c')
			return

		search_query = original_query.lower().replace(' ', '-')
		try:
			# EDHREC ordering is roughly by popularity, with most popular at the top
			start_time = time.time()
			#print('started sending request!')
			search_raw_data = requests.get(f"https://api.scryfall.com/cards/search?q={search_query}&order=edhrec")
			#print(f'finished fetching request in {time.time() - start_time} seconds')
			raw_json_dict = search_raw_data.json()
			raw_data_df = pd.json_normalize(raw_json_dict['data'])
		except:
			UpdateLabel.report('No cards found :c')
			return

		# First look for if there is an exact match; capitalization doesn't matter
		exact_matches_df = raw_data_df[raw_data_df['name'].str.lower() == original_query.lower()]
		if exact_matches_df.shape[0] != 0:
		# If no exact match, then just pick the most popular
			target_card_series = exact_matches_df.iloc[0]
		else:
			target_card_series = raw_data_df.iloc[0]

		target_category = self.get_curr_category()
		target_card_row = SetParsing.process_raw_card_series(target_card_series, target_category)
		
		target_card_name = target_card_row.index[0]
		UpdateLabel.report(f'Matched with "{target_card_name}" c:')

		return target_card_row
#----------------------------------------------------------------------------------------------------#
	def _output_new_cat_entries(self):
		keybind = self.keybind_entry.get().strip()
		name = self.cat_name_entry.get().strip()
		if len(keybind) == 0 or len(name) == 0:
			UpdateLabel.report('Invalid keybind and/or category name :c')
			raise Exception("No input for keybind and/or name")

		self.keybind_entry.delete(0, tk.END)
		self.cat_name_entry.delete(0, tk.END)
		UpdateLabel.report(f'{name} category added, using ({keybind}) to swap c:')
		return (keybind, name)
#----------------------------------------------------------------------------------------------------#
	def add_new_item(self):
		print("trying to add new item!")
		new_item_row = self._output_card_search()

		if new_item_row is None:
			return
		new_item_name = new_item_row.index[0]
		if CardCatManager.contains(new_item_name):
			UpdateLabel.report(f'{new_item_name} is already added :S')
			return

		CardCatManager.add_card(new_item_row)
#----------------------------------------------------------------------------------------------------#
	def add_custom_category(self):
		# Get custom category information
		try:
			(keybind, name) = self._output_new_cat_entries()
		except Exception as e:
			return

		if CardCatManager.contains_keybind(keybind):
			UpdateLabel.report(f"'{keybind}' already being used :c")
			return
		
		CardCatManager.add_category(keybind, name)
#----------------------------------------------------------------------------------------------------#
	def reorganize_cat_blocks(self):
		# Clear the menu
		self.category_menu['menu'].delete(0, tk.END)
		
		# Add categories in the updated order
		if CardCatManager.categories_df.shape[0] == 0:
			return
		category_names_list = CardCatManager.categories_df['name'].to_list()
		for category_name in category_names_list:
			self.category_menu['menu'].add_command(
				label=category_name,
				command=tk._setit(self.target_category, category_name)
			)
		
		# Set target_category to first category if not set to anything 
		if not self.target_category.get():
			self.target_category.set(category_names_list[0])







