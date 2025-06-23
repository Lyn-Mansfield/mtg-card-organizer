import numpy as np
import pandas as pd
from tkinter import *
import requests

root = Tk()
root.title("Search Tool")
# set default window size
root.geometry("800x600")

title_label = Label(root, text='Search for your MTG cards!')
title_label.pack(fill=X, padx=5, pady=5)

search_frame = Frame(root)
search_frame.pack(fill=X, padx=5, pady=5)

search_entry = Entry(search_frame)
search_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))

# initialize undo/redo vars
undo_move, redo_move = (), ()

def search():
	original_query = search_entry.get().strip()
	search_entry.delete(0, END)
	if len(original_query) == 0:
		update_label.config(text='Empty query :c')
		return

	search_query = original_query.replace(' ', '-')
	
	try:
		# edhrec ordering is roughly by popularity, with most popular at the top
		search_raw_data = pd.read_json(f"https://api.scryfall.com/cards/search?q={search_query}&order=edhrec")
	except:
		update_label.config(text='No cards found :c')
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
	search_listbox.insert(END, target_card_name)

	global undo_move; global redo_move
	undo_move = ('add', target_card_name, search_listbox.index("end"))
	redo_move = ()
	update_label.config(text=f'Added "{target_card_name}" c:')

search_button = Button(search_frame, text="Search", command=search)
search_button.pack(side=LEFT)

search_entry.bind('<Return>', lambda event: search())  # search on Enter key

update_label = Label(root, text='')
update_label.pack(fill=X)

list_frame = Frame(root)
list_frame.pack(fill=BOTH, expand=True, padx=5, pady=(0, 5))
list_frame.columnconfigure(0, weight=1)

search_listbox = Listbox(list_frame,relief="flat")
search_listbox.pack(side=LEFT, fill=BOTH, expand=True)

search_list_scrollbar = Scrollbar(list_frame, orient=VERTICAL, command=search_listbox.yview)
search_list_scrollbar.pack(side=RIGHT, fill=Y)
search_listbox.configure(yscrollcommand=search_list_scrollbar.set)

def searchbox_undo(event=None):
	global undo_move; global redo_move
	if undo_move == ():
		return
	action_performed, entry, index = undo_move[0], undo_move[1], undo_move[2]
	if action_performed == 'add':
		search_listbox.delete(index)
		redo_move = ('remove', entry, index)
		update_label.config(text=f'"{entry}" removed!')
	if action_performed == 'remove':
		search_listbox.insert(index, entry)
		redo_move = ('add', entry, index)
		update_label.config(text=f'"{entry}" readded!')
	undo_move = ()

# bind ctrl+z to the root window
root.bind('<Control-z>', searchbox_undo)
root.bind('<Control-Z>', searchbox_undo)  # handles case where caps lock is on
# for Mac users (cmd+z instead of ctrl+z)
root.bind('<Command-z>', searchbox_undo)
root.bind('<Command-Z>', searchbox_undo)

def delete_selected_entry(event=None):
	selected_index = search_listbox.curselection()

	global undo_move; global redo_move
	undo_move = ('remove', search_listbox.get(selected_index), selected_index)
	redo_move = ()

	update_label.config(text=f'"{search_listbox.get(selected_index)}" removed!')
	search_listbox.delete(selected_index)

root.bind('<Delete>', delete_selected_entry)
root.bind('<BackSpace>', delete_selected_entry)

root.mainloop()