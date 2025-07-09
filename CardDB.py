import tkinter as tk
import pandas as pd
from UpdateLabel import UpdateLabel

class CardDB:
    # Card name set as index
    cards_df = pd.DataFrame()

    # Category/Keybind storage
    keys_and_cats = {}
    names_and_cats = {}

    @classmethod
    def contains(cls, name_query):
        if cls.cards_df.shape[0] == 0:
            return False
        print(name_query)
        return name_query in cls.cards_df.index

    @classmethod
    def find(cls, name_query):
        if not cls.contains(name_query):
            return None
        return cls.cards_df.query("name == @name_query")

    @classmethod
    def add(cls, row_df):
        if type(row_df) != pd.DataFrame:
            raise TypeError("Rows to be added must be DataFrame")
        # Rows will come in without the name set as index, so we set the name as index each time
        cls.cards_df = pd.concat([cls.cards_df, row_df])
        cls.cards_df.set_index('name')

    @classmethod
    def delete(cls, name):
        if not cls.contains(name):
            raise KeyError(f"{name} not found in database")
        cls.cards_df.drop(name, inplace=True)

    @classmethod
    def transfer(cls, old_cat_block, keybind):
        if keybind not in cls.keys_and_cats.keys() or old_cat_block.size() == 0:
            return
        new_cat_block = cls.keys_and_cats[keybind]

        print(f"name of new cat block: {new_cat_block.name}")
        print(f"name of old cat block: {old_cat_block.name}")

        selected_card_row = old_cat_block.selected_row()
        selected_card_name = selected_card_row.index[0]

        # Remove from current block, transfer to new block
        old_cat_block.delete(selected_card_name)
        new_cat_block.insert(selected_card_row)
        cls.cards_df.loc[selected_card_name, 'main_category'] = new_cat_block
        # Go to the card after it's been moved
        new_cat_block.goto(tk.END)

        UpdateLabel.report(f"{selected_card_name} moved from {old_cat_block.name} to {new_cat_block.name} c:")

    @classmethod
    def update_count(cls, card_name, difference):
        if not cls.contains(card_name):
            return
        cls.cards_df.loc[card_name, 'count'] += difference

    @classmethod
    def add_category(cls, keybind, category_name, new_cat_block):
        cls.keys_and_cats[keybind] = new_cat_block
        cls.names_and_cats[category_name] = new_cat_block

    @classmethod
    def delete_category(cls, category_name):
        deleted_cat_block = cls.names_and_cats[category_name]
        deleted_keybind = deleted_cat_block.keybind

        del cls.keys_and_cats[deleted_keybind]
        del cls.names_and_cats[category_name]
        deleted_cat_block.destroy()
