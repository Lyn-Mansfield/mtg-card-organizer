import json
import requests
import time

import random
import string

from tkinter import filedialog
from pathlib import Path

import regex as re
import pandas as pd
import numpy as np
from CardCatManager import CardCatManager
from UpdateLabel import UpdateLabel
#----------------------------------------------------------------------------------------------------#
# Captures 1. the count of a card, 2. the name, 3. the set number, and 4. the categories, if given
card_line_regex = r"^(\d+)x? ([\w\s,'-/]+) \(([[a-zA-Z0-9]+)\) ?(\[.+\])?"
def create_card_row(line, main_cat):
	if '{' in line:
		tags = re.search(r"{(.+)}", line)
		line = re.sub(r"{.+}", "", line)
	card_regex = re.match(card_line_regex, line)
	
	# Extract categories info, with main_cat being the first one in the list
	try:
		categories = card_regex[4]
		categories_list = categories[1:-1].split(',')
	except:
		categories_list = [] if main_cat is None else [main_cat]

	count, name, set_code = card_regex[1], card_regex[2], card_regex[3]
	if main_cat is None and len(categories_list) > 0:
		main_cat = categories_list[0]

	return pd.DataFrame({
		'name': [name],
		'set_code': [set_code.upper()],
		'count': [count],
		'main_category': [main_cat],
		'all_categories': [categories_list]
	})
#----------------------------------------------------------------------------------------------------#
def _generate_post_request(df):
	
	def make_row_json(row):
		name, set_code = row['name'], row['set_code']
		# Split cards gunk up, but searching on just the first card name works
		searchable_name = name if '//' not in name else name.split('//')[0].strip()
		return f'{{"name": "{searchable_name}", "set": "{set_code}"}}'
	
	card_json_series = df.apply(lambda row: make_row_json(row), axis=1)
	card_json_str = card_json_series.str.cat(sep=',\n	')
	full_json_str = f'{{"identifiers": [\n	{card_json_str}\n]}}'

	return json.loads(full_json_str)
#----------------------------------------------------------------------------------------------------#	
def _find_suitable_keybind(cat_name):
	# If no suitable keybind is found, just find a random one
	if len(cat_name) == 0:
		random_char = random.choice(string.ascii_lowercase)
		while CardCatManager.contains_keybind(random_char):
			random_char = random.choice(string.ascii_letters)
		return random_char

	first_char = cat_name[0]
	# If it's not a letter, then skip to the next character
	if not first_char.isalpha():
		return _find_suitable_keybind(cat_name[1:])
	# Try lowercase lettering, then uppercase
	lower_first_char = first_char.lower()
	if not CardCatManager.contains_keybind(lower_first_char):
		return lower_first_char
	upper_first_char = first_char.upper()
	if not CardCatManager.contains_keybind(upper_first_char):
		return upper_first_char
	# If neither works, try again with the next character
	return _find_suitable_keybind(cat_name[1:])
#----------------------------------------------------------------------------------------------------#	
MAX_POST_REQUEST_SIZE = 50
def process_card_info_list(card_info_list):
	raw_cards_data_df = pd.DataFrame()
	# Divide list into blocks of 50
	for g, block_df in card_info_list.groupby(np.arange(len(card_info_list)) // MAX_POST_REQUEST_SIZE):
		# Transform blocks into scryfall API post json
		post_json = _generate_post_request(block_df)
		
		# Post request, process response and add in additional info from card_info_list
		search_raw_data = requests.post("https://api.scryfall.com/cards/collection", json=post_json)
		raw_json_dict = search_raw_data.json()
		raw_data_df = pd.json_normalize(raw_json_dict['data'])

		# Add count and category info
		# Reset the indices so that they align with the ones in raw_data_df
		raw_data_df['count'] = block_df['count'].reset_index(drop=True).astype(int)
		raw_data_df['main_category'] = block_df['main_category'].reset_index(drop=True)
		raw_data_df['all_categories'] = block_df['all_categories'].reset_index(drop=True)

		raw_cards_data_df = pd.concat([raw_cards_data_df, raw_data_df], ignore_index=True)
		# Wait 0.1 seconds as a courtesy to Scryfall API
		time.sleep(0.1)

	# Find all unique categories, and then add them
	unique_categories = card_info_list['all_categories'].explode().unique().tolist()
	for category_name in unique_categories:
		suitable_keybind = _find_suitable_keybind(category_name)
		CardCatManager.add_category(suitable_keybind, category_name)

	# Process all card rows
	processed_card_rows_list = raw_cards_data_df.apply(lambda row: process_raw_card_series(row, row['main_category'], count=row['count'], all_cats=row['all_categories']), axis=1).to_list()
	# Insert all the cards
	for processed_card_row in processed_card_rows_list:
		CardCatManager.add_card(processed_card_row)
#----------------------------------------------------------------------------------------------------#
# Returns a cleaned DataFrame row of processed card info
def process_raw_card_series(card_series, main_cat, count=1, all_cats=None):
	# Some cards have flavor names, which should be used since that's what appears on the card art
	if 'flavor_name' in card_series.index:
		card_series = card_series.rename(card_series['flavor_name'])
	else:
		card_series = card_series.rename(card_series['name'])

	# Avoid 'editing values of a slice' warnings by working with a clean copy
	card_series = card_series.copy()

	card_series['count'] = count
	card_series['date_added'] = time.time()

	# Some cards like lands won't have power/toughness values, which is OK
	try:
		power_str, toughness_str = card_series['power'], card_series['toughness']
		card_series['power'] = int(power_str)
		card_series['toughness'] = int(toughness_str)
	except (ValueError, KeyError) as e:
		pass
	
	card_series['main_category'] = main_cat
	if all_cats is not None:
		card_series['all_categories'] = all_cats
	else:
		card_series['all_categories'] = [main_cat]

	# Dual cards can't flip, but double-sided cards can
	if 'image_uris.png' in card_series.index:
		card_series['flips'] = False
	else:
		card_series['flips'] = True

	# Handle double-sided cards and dual cards (i.e. rooms)
	# Stores each side's info as DataFrames
	if 'card_faces' in card_series.index and card_series['card_faces'] is not np.nan:
		card_faces_info = card_series['card_faces']
		front_side_json, back_side_json = card_faces_info[0], card_faces_info[1]
		card_series['first_card_info'] = pd.json_normalize(front_side_json)
		card_series['second_card_info'] = pd.json_normalize(back_side_json)

	# Turn into a one-row DataFrame 
	return card_series.to_frame().T
#----------------------------------------------------------------------------------------------------#	
def read_txt_deck(txt_file_link):
	card_info_list = pd.DataFrame()

	user_accepts = CardCatManager.destroy_all_categories()
	if not user_accepts:
		return

	with open(txt_file_link) as decklist_file:
		decklist_lines = decklist_file.readlines()
		previous_line = None
		overarching_category = None
		for line in decklist_lines:
			if previous_line is None:
				is_category_line = line[0].isalpha()
				if is_category_line:
					overarching_category = line.replace('\n', '')
				else:
					new_card_row = create_card_row(line, overarching_category)
					card_info_list = pd.concat([card_info_list, new_card_row], ignore_index=True)
				previous_line = line
				continue

			# Category headers are preceded by blank new-lines
			if previous_line == "\n":
				overarching_category = line.replace('\n', '')
			elif line != "\n":
				new_card_row = create_card_row(line, overarching_category)
				card_info_list = pd.concat([card_info_list, new_card_row], ignore_index=True)
			previous_line = line

	process_card_info_list(card_info_list)
#----------------------------------------------------------------------------------------------------#	
def import_deck():
	decklist_file_path = filedialog.askopenfilename()
	extension = decklist_file_path[-3:]

	successfully_processed = False
	match extension:
		case 'txt':
			successfully_processed = True
		case _:
			UpdateLabel.report(".txt only plz xc")
			return

	if successfully_processed:
		UpdateLabel.report(f"Successfully processed {decklist_file_path} cx")

	CardCatManager.decklist_file_path = decklist_file_path
	read_txt_deck(decklist_file_path)
#----------------------------------------------------------------------------------------------------#	
def export_deck():
	file_path = filedialog.asksaveasfilename(
		defaultextension=".txt",
		filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
		title="Save as Text File"
	)

	# If no file path chosen, then do nothing
	if not file_path:
		return

	card_rows_str_series = CardCatManager.cards_df.apply(lambda row: f"{row['count']}x {row['name']} ({row['set']}) [{', '.join(row['all_categories'])}]", axis=1)
	card_rows_full_str = '\n'.join(card_rows_str_series)

	file_path = Path(file_path).with_suffix('.txt')
	try:
		file_path.write_text(card_rows_full_str, encoding='utf-8')
		print(f"Successfully saved to {file_path}")
	except Exception as e:
		print(f"Error saving file: {e}")