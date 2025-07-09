import tkinter as tk
import pandas as pd

class CardDB:
	# Card name set as index
	cards_df = pd.DataFrame()

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
	def transfer(cls, old_cat_block, new_cat_block):
		selected_card_row = old_cat_block.selected_row(selected_index)
		selected_card_name = selected_card_row.index[0]

		# Remove from current block, transfer to new block
		old_cat_block.delete(selected_card_name)
		new_cat_block.insert(selected_card_row)
		cls.cards_df.loc[selected_card_name, 'main_category'] = new_cat_block
		# Go to the card after it's been moved
		new_cat_block.goto(tk.END)

	@classmethod
	def update_count(cls, card_name, difference):
		if not cls.contains(card_name):
			return
		cls.cards_df.loc[card_name, 'count'] += difference
