import tkinter as tk
import pandas as pd
import time
from UpdateLabel import UpdateLabel
from SidebarFrame import SidebarFrame

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
		if len(cls.keys_and_cats) == 0:
			return False
		return keybind_query in cls.keys_and_cats.keys()
#----------------------------------------------------------------------------------------------------#
	@classmethod
	def contains_cat_name(cls, cat_name_query):
		if len(cls.names_and_cats) == 0:
			return False
		return cat_name_query in cls.names_and_cats.keys()
#----------------------------------------------------------------------------------------------------#
	# Return card Series of the same name
	@classmethod
	def find(cls, name_query):
		if not cls.contains(name_query):
			return None
		return cls.cards_df.loc[name_query]
#----------------------------------------------------------------------------------------------------#
	@classmethod
	def _update_sizes(cls):
		cls.categories_df['size'] = cls.categories_df.index.map(lambda cat_block: cat_block.size())
		cls._update_block_frames()
#----------------------------------------------------------------------------------------------------#
	# WIP
	@classmethod
	def _update_block_frames(cls):
		return
		cat_order = SidebarFrame.cat_order()
		match cat_order:
			case 'Alphabetical':
				# Might sort by index by default? unsure
				cls.categories_df.sort_values()
			case 'Size':
				cls.categories_df.sort_values(by='size')
			case 'Type':
				cls._sort_by_type()
			case 'Color':
				cls._sort_by_color()
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
	# Returns a list of cat block objects, sorted in the order they should be inserted
	@classmethod
	def sorted_cat_order(cls):
		return cls.categories_df.index.to_list()
#----------------------------------------------------------------------------------------------------#
	@classmethod
	def add_card(cls, new_card_row):
		if type(new_card_row) != pd.DataFrame:
			raise TypeError("Rows to be added must be DataFrame")
		# Rows will come in with the name set as index
		cls.cards_df = pd.concat([cls.cards_df, new_card_row])
		
		target_cat_name = new_card_row['main_category'].iloc[0]
		target_cat_block = cls.names_and_cats[target_cat_name]
		target_cat_block.insert(new_card_row)
		
		cls._update_sizes()
#----------------------------------------------------------------------------------------------------#
	@classmethod
	def remove_card_from_cat(cls, cat_block, card_name):
		if not cls.contains(card_name):
			raise KeyError(f"{card_name} not found in database")
		
		# Remove current category from this card's list of all categories
		cls.cards_df.loc[card_name, 'all_categories'].remove(cat_block.name)
		UpdateLabel.report(f"Removed {card_name} from {cat_block.name}")

		has_no_remaining_categories = len(cls.cards_df.loc[card_name, 'all_categories']) == 0
		print(cls.cards_df.loc[card_name, 'all_categories'], has_no_remaining_categories)
		removed_from_main_category = cls.cards_df.loc[card_name, 'main_category'] == cat_block.name
		print(cls.cards_df.loc[card_name, 'main_category'], cat_block.name, removed_from_main_category)
		if has_no_remaining_categories or removed_from_main_category:
			cls.delete_card(card_name)
		cls._update_sizes()
#----------------------------------------------------------------------------------------------------#
	@classmethod
	def delete_card(cls, card_name):
		if not cls.contains(card_name):
			raise KeyError(f"{card_name} not found in database")

		cls.cards_df.drop(card_name, inplace=True)
		UpdateLabel.report(f"Deleted {card_name} from the whole deck")
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
	def transfer_main_category(cls, old_cat_block, keybind):
		if keybind not in cls.keys_and_cats.keys() or old_cat_block.size() == 0:
			return

		new_cat_block = cls.keys_and_cats[keybind]
		selected_card_series = old_cat_block.selected_row()
		selected_card_row = selected_card_series.to_frame().T
		selected_card_name = selected_card_series.name

		# Set the new cat block as the main category
		cls.cards_df.loc[selected_card_name, 'main_category'] = new_cat_block.name

		# If the card only lived in the main category, then transfer over to new main category
		if len(cls.cards_df.loc[selected_card_name, 'all_categories']) == 1:
			cls.cards_df.loc[selected_card_name, 'all_categories'].append(new_cat_block.name)
			new_cat_block.insert(selected_card_row)
			old_cat_block.delete(selected_card_name)
		# If the card hasn't already been added to the new block, then add it
		if new_cat_block.name not in cls.cards_df.loc[selected_card_name, 'all_categories']:
			cls.cards_df.loc[selected_card_name, 'all_categories'].append(new_cat_block.name)
			new_cat_block.insert(selected_card_row)

		# Go to the card after it's been moved
		new_cat_block.goto(tk.END)

		UpdateLabel.report(f"{selected_card_name} moved from {old_cat_block.name} to {new_cat_block.name} c:")
		cls._update_block_frames()
#----------------------------------------------------------------------------------------------------#
	@classmethod
	def add_secondary_category(cls, old_cat_block, keybind):
		if keybind not in cls.keys_and_cats.keys() or old_cat_block.size() == 0:
			return

		new_cat_block = cls.keys_and_cats[keybind]
		selected_card_series = old_cat_block.selected_row()
		selected_card_name = selected_card_series.name
		cls.cards_df.loc[selected_card_name, 'all_categories'].append(new_cat_block.name)

		# Add to new block
		selected_card_row = selected_card_series.to_frame().T
		new_cat_block.insert(selected_card_row)

		UpdateLabel.report(f"{selected_card_name} added to {new_cat_block.name} as a secondary category c:")
		cls._update_block_frames()
#----------------------------------------------------------------------------------------------------#
	# Adds a category to the db, linking it to its keybind and name for easy searching
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
		
		cls._update_block_frames()
#----------------------------------------------------------------------------------------------------#
	# Removes a category from the db, including all cards in the category
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

		cls._update_block_frames()
#----------------------------------------------------------------------------------------------------#
	@classmethod
	def update_keybind(cls, old_keybind, new_keybind, cat_block):
		assert cls.contains_keybind(old_keybind)
		assert not cls.contains_keybind(new_keybind)
		
		del cls.keys_and_cats[old_keybind]
		cls.keys_and_cats[new_keybind] = cat_block
#----------------------------------------------------------------------------------------------------#
	@classmethod
	def update_cat_name(cls, old_name, new_name, cat_block):
		assert cls.contains_cat_name(old_name)
		assert not cls.contains_cat_name(new_name)
		
		del cls.names_and_cats[old_name]
		cls.names_and_cats[new_name] = cat_block

		cls._update_block_frames()
