import pandas as pd
import tkinter as tk
from tkinter import ttk

class CardEntryFrame:
    def __init__(self, root, add_item_command=None, add_cat_command=None, highlightbackground=None, highlightthickness=None):
        # Whole frame, thing everything is inside of
        self.whole_frame = tk.Frame(
            root, 
            highlightbackground=highlightbackground, 
            highlightthickness=highlightthickness
        )

        # Entries frame
        self.entries_frame = tk.Frame(
            self.whole_frame, 
            highlightbackground='brown', 
            highlightthickness=2
        )
        self.entries_frame.pack(side=tk.TOP, expand=True, fill=tk.X, padx=10, pady=5)

        # Card entry
        self.card_entry = ttk.Entry(self.entries_frame)
        self.card_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        self.card_entry.bind('<Return>', add_item_command)

        # Category Selection Menu
        self.target_category = tk.StringVar(value="Unsorted")
        self.category_menu = ttk.OptionMenu(
            self.entries_frame, self.target_category, *[], command=lambda _: self.card_entry.focus()
        )
        self.category_menu.pack(side=tk.LEFT, padx=(0, 5))

        # Custom category frame
        self.add_cat_frame = tk.Frame(
            self.entries_frame, 
            highlightbackground='silver', 
            highlightthickness=2
        )
        self.add_cat_frame.pack(side=tk.LEFT, fill=tk.X)

        # Custom category entry
        one_char_validation = (self.whole_frame.register(self._validate_one_char), '%P')
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

        # Update label
        self.update_label = tk.Label(self.whole_frame, text='')
        self.update_label.pack(side=tk.BOTTOM, expand=True, fill=tk.X)
#----------------------------------------------------------------------------------------------------#
    def _validate_one_char(self, P):
        if len(P) <= 1:
            return True
        else:
            return False
#----------------------------------------------------------------------------------------------------#
    def pack(self, side=None, padx=None, pady=None, expand=False, fill=None):
        self.whole_frame.pack(side=side, padx=padx, pady=pady, expand=expand, fill=fill)
#----------------------------------------------------------------------------------------------------#
    def get_curr_category(self):
        return self.target_category.get()
#----------------------------------------------------------------------------------------------------#
    def output_card_search(self):
        original_query = self.card_entry.get()
        self.card_entry.delete(0, tk.END)
        if len(original_query) == 0:
            self.update_label.config(text='Empty query :c')
            return

        search_query = original_query.lower().replace(' ', '-')
        try:
            # edhrec ordering is roughly by popularity, with most popular at the top
            search_raw_data = pd.read_json(f"https://api.scryfall.com/cards/search?q={search_query}&order=edhrec")
        except:
            self.update_label.config(text='No cards found :c')
            return

        raw_card_data_series = search_raw_data.apply(lambda row: pd.json_normalize(row['data']), axis=1)
        raw_card_data_df = pd.concat(raw_card_data_series.tolist())
        try:
            # first look for if there is an exact match
            raw_card_data_df['search_name'] = raw_card_data_df['name'].str.lower()
            raw_card_data_df = raw_card_data_df.set_index('search_name')
            target_card_row = raw_card_data_df.loc[original_query.lower()]
        except:
            # if no exact match, then just pick the most popular
            target_card_row = raw_card_data_df.iloc[0]
        
        target_card_name = target_card_row['name']
        self.update_label.config(text=f'Matched with "{target_card_name}" c:')
        return target_card_name
#----------------------------------------------------------------------------------------------------#
    def output_new_cat_entries(self):
        keybind = self.keybind_entry.get().strip()
        name = self.cat_name_entry.get().strip()
        if len(keybind) == 0 or len(name) == 0:
            self.update_label.config(text='Invalid keybind and/or category name :c')
            raise Exception("No input for keybind and/or name")

        self.keybind_entry.delete(0, tk.END)
        self.cat_name_entry.delete(0, tk.END)
        self.update_label.config(text=f'{name} category added, using ({keybind}) to swap c:')
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









