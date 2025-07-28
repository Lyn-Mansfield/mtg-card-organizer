import tkinter as tk
from tkinter import messagebox
import pandas as pd
import time
from UpdateLabel import UpdateLabel

class CardCatManager:
	# Card name set as index
	cards_df = pd.DataFrame()
	categories_df = pd.DataFrame()

	cat_blocks = []
	card_entry_frame = None
	block_frame = None

	# Actual defaults live in SidebarFrame
	primary_only = None
	cat_order = None
	block_order = None
#----------------------------------------------------------------------------------------------------#
	# Update card DB when SidebarFrame variables change, and then reload the block frame to reflect changes
	@classmethod
	def _update_class_vars(cls, primary_only, cat_order, block_order):
		cls.primary_only = primary_only
		cls.cat_order = cat_order
		cls.block_order = block_order

		cls._update_block_frames()
#----------------------------------------------------------------------------------------------------#
	@classmethod
	def print_db(cls):
		print(f"Central DB:\n{cls.cards_df[['main_category', 'all_categories','count']]}")
#----------------------------------------------------------------------------------------------------#
	@classmethod
	def contains(cls, name_query):
		if cls.cards_df.shape[0] == 0:
			return False
		return name_query in cls.cards_df.index
#----------------------------------------------------------------------------------------------------#
	@classmethod
	def contains_keybind(cls, keybind_query):
		if cls.categories_df.shape[0] == 0:
			return False
		return cls.categories_df.keybind.isin([keybind_query]).any()
#----------------------------------------------------------------------------------------------------#
	@classmethod
	def contains_cat_name(cls, cat_name_query):
		if cls.categories_df.shape[0] == 0:
			return False
		return cls.categories_df.name.isin([cat_name_query]).any()
#----------------------------------------------------------------------------------------------------#
	# Returns DataFrame of all card rows that have a category in all_categories
	# Returned in order it should be inserted
	@classmethod
	def sorted_relevant_card_rows(cls, category_name):
		# If no cards have been added, return an empty DataFrame
		if cls.cards_df.shape[0] == 0:
			return pd.DataFrame()
		relevant_card_rows = cls.cards_df[cls.cards_df['all_categories'].apply(lambda x: category_name in x)]

		match cls.block_order:
			case 'Alphabetical':
				return relevant_card_rows.sort_index()
			case 'Mana Cost':
				return relevant_card_rows.sort_values(by='cmc', na_position='first')
			case 'Date Added':
				return relevant_card_rows.sort_values(by='date_added')
			case 'Number':
				return relevant_card_rows.sort_values(by='count')
			case 'Power':
				return relevant_card_rows.sort_values(by='power', na_position='first')
			case 'Toughness':
				return relevant_card_rows.sort_values(by='toughness', na_position='first')
#----------------------------------------------------------------------------------------------------#
	# Return card Series of the same name
	@classmethod
	def find(cls, name_query):
		if not cls.contains(name_query):
			return None
		return cls.cards_df.loc[name_query]

	@classmethod
	def reorganize_cat_blocks(cls):
		if cls.card_entry_frame is not None:
			cls.card_entry_frame.reorganize_cat_blocks()
		if cls.block_frame is not None:
			cls.block_frame.reorganize_cat_blocks()
#----------------------------------------------------------------------------------------------------#
	# Reorganizes by size of the 
	@classmethod
	def _update_block_frames(cls, focus_card=None, focus_cat_name=None):
		if cls.categories_df.shape[0] == 0:
			cls.reorganize_cat_blocks()
			return

		match cls.cat_order:
			case 'Date Added':
				cls.categories_df.sort_values(by='date_added', inplace=True)
			case 'Alphabetical':
				cls.categories_df.sort_values(by='name', inplace=True)
			case 'Size':
				cls.categories_df.sort_values(by='size', ascending=False, inplace=True)
			case 'Type':
				cls._sort_by_type()
			case 'Color':
				cls._sort_by_color()

		cls.reorganize_cat_blocks()

		# Update category sizes
		cls.categories_df['size'] = cls.categories_df['cat_block'].apply(lambda cat_block: 0 if cat_block is None else cat_block.size())

		# Highlight card, if specified
		if focus_card is None or focus_cat_name is None:
			return

		categories_indexed_by_name = cls.categories_df.set_index('name')
		focus_cat_block = categories_indexed_by_name.loc[focus_cat_name, 'cat_block']
		focus_cat_block.focus(focus_card)

	# WIP
	@classmethod
	def _sort_by_type(cls):
		type_blocks_dict = {}
		# group by type
			# if multiple types, make first one primary
		# create a cat block for each of those types
		# broadcast to cat block frame
		cards_df.groupby('Type').show()

		if types_block_name not in type_blocks_dict.keys():
			new_type_block = CategoryBlock()
#----------------------------------------------------------------------------------------------------#
	# Returns a list of cat block Series, sorted in the order they should be inserted
	@classmethod
	def sorted_cat_order(cls):
		row_list = []
		for index, row in cls.categories_df.iterrows():
			row_list.append(row)
		return row_list
#----------------------------------------------------------------------------------------------------#
	@classmethod
	def add_card(cls, new_card_row):
		if type(new_card_row) != pd.DataFrame:
			raise TypeError("Rows to be added must be DataFrame")
		# Rows will come in with the name set as index
		cls.cards_df = pd.concat([cls.cards_df, new_card_row])
		
		cls._update_block_frames()
#----------------------------------------------------------------------------------------------------#
	# Updates the count of a card, only meant to handle when a card's count doesn't go below 0
	# Otherwise card is slated to be deleted, as detailed in CategoryBlock.update_count(difference)
	@classmethod
	def _update_count(cls, card_name, difference, cat_name):
		cls.cards_df.loc[card_name, 'count'] += difference
		if cls.cards_df.loc[card_name, 'count']  <= 0:
			raise ValueError("Trying to remove more cards than there are, should be deleted instead!")
		cls._update_block_frames(focus_card=card_name, focus_cat_name=cat_name)
#----------------------------------------------------------------------------------------------------#
	@classmethod
	def remove_card_from_cat(cls, cat_block, card_name):
		if not cls.contains(card_name):
			raise KeyError(f"{card_name} not found in database")
		
		# Remove current category from this card's list of all categories
		cls.cards_df.loc[card_name, 'all_categories'].remove(cat_block.name)
		UpdateLabel.report(f"Removed {card_name} from {cat_block.name}")

		has_no_remaining_categories = len(cls.cards_df.loc[card_name, 'all_categories']) == 0
		removed_from_main_category = cls.cards_df.loc[card_name, 'main_category'] == cat_block.name
		if has_no_remaining_categories or removed_from_main_category:
			cls.delete_card(card_name)

		cls._update_block_frames()
#----------------------------------------------------------------------------------------------------#
	@classmethod
	def delete_card(cls, card_name):
		if not cls.contains(card_name):
			raise KeyError(f"{card_name} not found in database")

		cls.cards_df.drop(card_name, inplace=True)
		UpdateLabel.report(f"Deleted {card_name} from the whole deck")
		cls._update_block_frames()
#----------------------------------------------------------------------------------------------------#
	@classmethod
	def transfer_main_category(cls, old_cat_block, keybind):
		if not cls.contains_keybind(keybind) or old_cat_block.size() == 0:
			return

		new_main_cat_name = cls.categories_df.query("keybind == @keybind")['name'].iloc[0]
		selected_card_series = old_cat_block.selected_row()
		selected_card_name = selected_card_series.name

		# Set the new cat block as the main category
		cls.cards_df.loc[selected_card_name, 'main_category'] = new_main_cat_name

		all_card_categories = cls.cards_df.loc[selected_card_name, 'all_categories']
		# If the card only lives in one category, then move it to the new main category
		if len(all_card_categories) == 1:
			cls.cards_df.loc[selected_card_name, 'all_categories'] = [new_main_cat_name]
			UpdateLabel.report(f"{selected_card_name} moved from {old_cat_block.name} to {new_main_cat_name} c:")
		elif new_main_cat_name not in all_card_categories:
			cls.cards_df.loc[selected_card_name, 'all_categories'].append(new_main_cat_name)
			UpdateLabel.report(f"{selected_card_name}'s primary category set to {new_main_cat_name} c:")
		cls._update_block_frames(focus_card=selected_card_name, focus_cat_name=new_main_cat_name)
#----------------------------------------------------------------------------------------------------#
	@classmethod
	def toggle_secondary_category(cls, cat_block, keybind):
		if not cls.contains_keybind(keybind) or cat_block.size() == 0:
			return
		# If the current cat block's keybind is pressed, then do nothing
		if cat_block.keybind == keybind:
			return

		categories_indexed_by_keybind = cls.categories_df.set_index('keybind')
		new_sub_cat_name = categories_indexed_by_keybind.loc[keybind, 'name']
		selected_card_series = cat_block.selected_row()
		selected_card_name = selected_card_series.name

		all_card_categories = cls.cards_df.loc[selected_card_name, 'all_categories']
		# If sub category is already in there, then remove it
		if new_sub_cat_name in all_card_categories:
			cls.cards_df.loc[selected_card_name, 'all_categories'].remove(new_sub_cat_name)
			UpdateLabel.report(f"{selected_card_name} removed from {new_sub_cat_name} as a secondary category c:")
		# Otherwise, add it
		else:
			cls.cards_df.loc[selected_card_name, 'all_categories'].append(new_sub_cat_name)
			UpdateLabel.report(f"{selected_card_name} added to {new_sub_cat_name} as a secondary category c:")
		cls._update_block_frames(focus_card=selected_card_name, focus_cat_name=cat_block.name)
#----------------------------------------------------------------------------------------------------#
	# Adds a category to the db, linking it to its keybind and name for easy searching
	@classmethod
	def add_category(cls, keybind, category_name):
		if cls.contains_keybind(keybind):
			UpdateLabel.report(f"'{keybind}' already being used :c")
			return

		new_cat_block_info_row = pd.DataFrame({
			'keybind': [keybind], 
			'name': [category_name],
			'date_added': [time.time()], 
			'size': [0],
			'cat_block': [None]
		})

		print(f"Adding category {category_name} ({keybind})")
		cls.categories_df = pd.concat([cls.categories_df, new_cat_block_info_row])
		
		cls._update_block_frames()
#----------------------------------------------------------------------------------------------------#
	# Removes a category from the db, including all cards in the category
	@classmethod
	def delete_category(cls, cat_block_to_delete):
		cls.categories_df.drop(cat_block_to_delete.keybind, inplace=True)

		# Remove this category from all cards assigned to this category
		for card_name in cat_block_to_delete.local_cards_df.index:
			cls.remove_card_from_cat(cat_block_to_delete, card_name)

		cls._update_block_frames()
#----------------------------------------------------------------------------------------------------#
	# Removes all categories and cards, usually in preparation for importing a decklist
	# Asks beforehand if this is ok
	@classmethod
	def destroy_all_categories(cls):
		user_accepts = messagebox.askyesno(
			"Deleting All Categories!", 
			"Are you sure you want to delete all current progress?", 
			icon='question'
		)
		if user_accepts:
			cls.cards_df = pd.DataFrame()
			cls.categories_df = pd.DataFrame()
			cls.destroy_all_blocks()

		cls._update_block_frames()
		return user_accepts
#----------------------------------------------------------------------------------------------------#
	@classmethod
	def destroy_all_blocks(cls):
		for cat_block in cls.cat_blocks:
			cat_block.destroy()
		cls.cat_blocks = []
#----------------------------------------------------------------------------------------------------#
	@classmethod
	def update_keybind(cls, new_keybind, cat_block):
		old_keybind = cat_block.keybind
		assert cls.contains_keybind(old_keybind)
		assert not cls.contains_keybind(new_keybind)
		
		cls.categories_df.loc[cls.categories_df['keybind'] == old_keybind, 'keybind'] = new_keybind

		cls._update_block_frames()
#----------------------------------------------------------------------------------------------------#
	@classmethod
	def update_cat_name(cls, new_name, cat_block):
		old_name = cat_block.name
		assert cls.contains_cat_name(old_name)
		assert not cls.contains_cat_name(new_name)
		
		cls.categories_df.loc[cls.categories_df['name'] == old_name, 'name'] = new_name

		cls._update_block_frames()
