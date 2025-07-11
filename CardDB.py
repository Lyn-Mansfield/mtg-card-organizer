import tkinter as tk
import pandas as pd
import time
from UpdateLabel import UpdateLabel

class CardDB:
    # Card name set as index
    cards_df = pd.DataFrame()
    categories_df = pd.DataFrame()

    # Category/Keybind storage
    keys_and_cats = {}
    names_and_cats = {}
#----------------------------------------------------------------------------------------------------#
    @classmethod
    def print_db(cls):
        print(f"Central DB:\n{cls.cards_df['count']}")
#----------------------------------------------------------------------------------------------------#
    @classmethod
    def contains(cls, name_query):
        if cls.cards_df.shape[0] == 0:
            return False
        return name_query in cls.cards_df.index
#----------------------------------------------------------------------------------------------------#
    @classmethod
    def find(cls, name_query):
        if not cls.contains(name_query):
            return None
        return cls.cards_df.query("name == @name_query")
#----------------------------------------------------------------------------------------------------#
    @classmethod
    def _update_sizes(cls):
    	cls.categories_df['size'] = cls.categories_df.index.map(lambda cat_block: cat_block.size())
#----------------------------------------------------------------------------------------------------#
    @classmethod
    def add_card(cls, cat_block, row_df):
        if type(row_df) != pd.DataFrame:
            raise TypeError("Rows to be added must be DataFrame")
        # Rows will come in with the name set as index
        cls.cards_df = pd.concat([cls.cards_df, row_df])
        cls._update_sizes()
#----------------------------------------------------------------------------------------------------#
    @classmethod
    def delete_card(cls, cat_block, name):
        if not cls.contains(name):
            raise KeyError(f"{name} not found in database")
        cls.cards_df.drop(name, inplace=True)
        cls._update_sizes()
#----------------------------------------------------------------------------------------------------#
    @classmethod
    def _update_reference(cls, old_cat_block, cat_block_clone):
    	keybind, name = cat_block_clone.keybind, cat_block_clone.name
    	cls.keys_and_cats[keybind] = cat_block_clone
    	cls.names_and_cats[name] = cat_block_clone
    	cls.categories_df.rename(index={old_cat_block:cat_block_clone},inplace=True)
#----------------------------------------------------------------------------------------------------#
    @classmethod
    def transfer_card(cls, old_cat_block, keybind):
        if keybind not in cls.keys_and_cats.keys() or old_cat_block.size() == 0:
            return
        new_cat_block = cls.keys_and_cats[keybind]

        selected_card_row = old_cat_block.selected_row()
        print(selected_card_row)
        selected_card_name = selected_card_row.index[0]

        # Remove from current block, transfer to new block
        old_cat_block.delete(selected_card_name)
        new_cat_block.insert(selected_card_row)

        # Reflect changes in cards_df
        cls.cards_df.loc[selected_card_name, 'main_category'] = new_cat_block
        # Go to the card after it's been moved
        new_cat_block.goto(tk.END)

        UpdateLabel.report(f"{selected_card_name} moved from {old_cat_block.name} to {new_cat_block.name} c:")
#----------------------------------------------------------------------------------------------------#
    @classmethod
    def add_category(cls, keybind, category_name, new_cat_block):
        cls.keys_and_cats[keybind] = new_cat_block
        cls.names_and_cats[category_name] = new_cat_block

        new_cat_block_info_row = pd.DataFrame({
        	'cat_block': [new_cat_block], 
        	'date_added': [time.time()], 
        	'size': [new_cat_block.size]
        })
        new_cat_block_info_row.set_index('cat_block', inplace=True)
        cls.categories_df = pd.concat([cls.categories_df, new_cat_block_info_row])
        # cls.sort()
#----------------------------------------------------------------------------------------------------#
    @classmethod
    def delete_category(cls, category_name):
        deleted_cat_block = cls.names_and_cats[category_name]
        deleted_keybind = deleted_cat_block.keybind

        del cls.keys_and_cats[deleted_keybind]
        del cls.names_and_cats[category_name]
        cls.categories_df.drop(new_cat_block, inplace=True)

        # Delete from the DB all cards that lived in that category
        for card_name in deleted_cat_block.local_cards_df.index:
        	cls.delete(card_name)

        deleted_cat_block.destroy()
