import pandas as pd
import tkinter as tk
import numpy as np
from tkinter import ttk
import requests
from UpdateLabel import UpdateLabel

class CardEntryFrame(tk.Frame):
    def __init__(self, root, add_item_command=None, add_cat_command=None, **kwargs):
        # Everything lives in self
        super().__init__(root, **kwargs)

        # Card entry
        self.card_entry = ttk.Entry(self)
        self.card_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        self.card_entry.bind('<Return>', add_item_command)

        # Category Selection Menu
        self.target_category = tk.StringVar(value="Unsorted")
        self.category_menu = ttk.OptionMenu(
            self, self.target_category, *[], command=lambda _: self.card_entry.focus()
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
        self.cat_name_entry.bind('<Return>', lambda _: add_cat_command())

        # Add button
        self.add_button = ttk.Button(
            self.add_cat_frame, text="Add", command=add_cat_command
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
    def output_card_search(self):
        original_query = self.card_entry.get()
        self.card_entry.delete(0, tk.END)
        if len(original_query) == 0:
            UpdateLabel.report('Empty query :c')
            return

        search_query = original_query.lower().replace(' ', '-')
        try:
            # EDHREC ordering is roughly by popularity, with most popular at the top
            search_raw_data = requests.get(f"https://api.scryfall.com/cards/search?q={search_query}&order=edhrec")
            raw_json_dict = search_raw_data.json()
            raw_data_df = pd.DataFrame.from_dict(raw_json_dict)
        except:
            UpdateLabel.report('No cards found :c')
            return

        raw_card_data_series = raw_data_df.apply(lambda row: pd.json_normalize(row['data']), axis=1)
        raw_card_data_df = pd.concat(raw_card_data_series.tolist())

        # First look for if there is an exact match; capitalization doesn't matter
        raw_card_data_df = raw_card_data_df.set_index('name')
        exact_matches_df = raw_card_data_df[raw_card_data_df.index.str.lower() == original_query.lower()]
        if exact_matches_df.shape[0] != 0:
            target_card_series = exact_matches_df.iloc[0]
        # If no exact match, then just pick the most popular
        else:
            target_card_series = raw_card_data_df.iloc[0]
        # Set the starting count to 1
        target_card_series['count'] = 1

        # Handle double-sided cards
        # Stores side info as DataFrames
        if 'card_faces' in target_card_series.index and target_card_series['card_faces'] is not np.nan:
            print(target_card_series['card_faces'])
            target_card_series['flips'] = True
            card_faces_info = target_card_series['card_faces']
            front_side_json, back_side_json = card_faces_info[0], card_faces_info[1]
            target_card_series['front_side_info'] = pd.json_normalize(front_side_json)
            target_card_series['back_side_info'] = pd.json_normalize(back_side_json)
            # target_card_row['front_info'] = 
        else:
            target_card_series['flips'] = False

        # Turn into a one-row DataFrame 
        target_card_row = target_card_series.to_frame().T
        
        target_card_name = target_card_row.index[0]
        UpdateLabel.report(f'Matched with "{target_card_name}" c:')

        return target_card_row
#----------------------------------------------------------------------------------------------------#
    def output_new_cat_entries(self):
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
    def add_category(self, keybind, name):
        # Update drop-down menu
        self.category_menu['menu'].add_command(
            label=name, 
            command=tk._setit(self.target_category, name)
        )
#----------------------------------------------------------------------------------------------------#
    def delete_category(self, category_name):
        self.category_menu['menu'].delete(category_name)

        # Update tracker variable if needed
        if self.target_category.get() == category_name:
            next_value = self.category_menu['menu'].entrycget(0, 'label')
            self.target_category.set(next_value)









