import tkinter as tk
from tkinter.font import Font 
import pandas as pd
import numpy as np
import requests

from tkinter import messagebox
from tkinter import simpledialog

from UpdateLabel import UpdateLabel
from CardCatManager import CardCatManager
from CardDisplayFrame import CardDisplayFrame

class CategoryBlock(tk.Frame):
    # Category block configuration
    min_width = 240
    min_height = 6
#----------------------------------------------------------------------------------------------------#
    def __init__(self, root, keybind, name):
        if not (isinstance(keybind, str) and isinstance(name, str)): 
            raise TypeError("keybind and name must be strings")

        super().__init__(root,
            highlightbackground='blue',
            height=300,
            width=self.min_width,
            highlightthickness=1
        )
        self.root = root

        self.top_frame = tk.Frame(self)
        self.top_frame.pack(side=tk.TOP, expand=True, fill=tk.X)

        # Category header
        self.keybind = keybind
        self.name = name
        self.header = tk.Label(self.top_frame)
        self.set_header_name()
        self.header.pack(side=tk.LEFT, expand=True)

        # Menu button and context menu
        self.menu_button = tk.Button(
            self.top_frame, 
            text="☰", 
            padx=0, pady=0,
            width=0,
            font=('Arial', 12),
            command=self.show_menu, 
            relief="flat"
        )
        self.menu_button.place(relx=1.0, rely=0.4, anchor='e')

        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="Rebind category", command=self.rebind)
        self.menu.add_command(label="Rename category", command=self.rename)
        self.menu.add_separator()
        self.menu.add_command(label="Print Local DB", command=lambda: print(self.local_cards_df[['main_category', 'all_categories', 'count', 'flips']]))
        self.menu.add_command(label="Print Card DB", command=CardCatManager.print_db)
        self.menu.add_separator()
        self.menu.add_command(label="Delete", command=self.ask_to_delete)

        # Cards listbox
        self.listbox = tk.Listbox(
            self,
            height=self.min_height
        )
        self.listbox.pack(side=tk.TOP, expand=True, fill=tk.X)
        prettier_font = Font(family="Book Antiqua", size=12, weight="bold")
        self.listbox.config(selectmode=tk.SINGLE, font=prettier_font)

        # Bind transfer command
        self.listbox.bind('<Button-1>', lambda event: self._on_click(event))
        self.listbox.bind('<<ListboxSelect>>', lambda event: self._on_select(event))
        self.listbox.bind('<Key>', lambda event: self._on_keystroke(event))

        # Adds all card rows from the card DB to the local DataFrame that live in this category 
        self.local_cards_df = CardCatManager.sorted_relevant_card_rows(self.name)

        self.fill_listbox()
#----------------------------------------------------------------------------------------------------#
    # Sets the focus on the current listbox
    def _on_click(self, event):
        self.listbox.update_idletasks()
        self.goto(tk.END)
#----------------------------------------------------------------------------------------------------#
    # Displays the selected card, if there is one selected
    def _on_select(self, event):
        self.listbox.update_idletasks()
        # If current listbox isn't being focused on, then we've clicked away and don't care
        if self.listbox is not self.root.focus_get():
            return
        selected_row = self.selected_row()
        print('displaying a new card!')
        CardDisplayFrame.display_new_image(selected_row)
        print('finished displaying')

        CardCatManager.focus_card = selected_row.name
        CardCatManager.focus_cat_name = self.name
#----------------------------------------------------------------------------------------------------#
    # Handles the different keystroke events we have defined, including card transfer
    def _on_keystroke(self, event):
        """Handle key presses for moving cards from category to category"""
        print('generic keystroke detected...')
        print(event.keysym)
        ctrl_state_code, ctrl_shift_state_code = 4, 5
        ctrl_being_held = event.state == ctrl_state_code
        ctrl_shift_being_held = event.state == ctrl_shift_state_code
        print(event.state, ctrl_being_held, ctrl_shift_being_held)

        match event.keysym:
            case "BackSpace" | "Delete":
                self.delete_selected_row()
            case "equal":
                self.add()
            case "plus":
                self.add_5()
            case "minus":
                self.subtract()
            case "underscore":
                self.subtract_5()
            case _ if ctrl_being_held or ctrl_shift_being_held:
                if ctrl_shift_being_held:
                    CardCatManager.toggle_secondary_category(self, event.keysym.upper())
                else:
                    CardCatManager.toggle_secondary_category(self, event.keysym)
            case _:
                CardCatManager.transfer_main_category(self, event.keysym)
#----------------------------------------------------------------------------------------------------#
    def set_header_name(self):
        self.header_name = f"{self.name} ({self.keybind})"
        self.header.configure(text=self.header_name)
#----------------------------------------------------------------------------------------------------#
    def rebind(self):
        # Open pop-up to rebind the specified label
        new_keybind = simpledialog.askstring(
            "Rebind", 
            "Enter new bind:",
            initialvalue=self.keybind,
            parent=self.winfo_toplevel()
        )
        # If no new keybind is given, exit 
        if not new_keybind:
            return
        # If new keybind is longer than one character, yell at user
        if len(new_keybind) > 1:
            UpdateLabel.report("Keybind must be one character long :S")
            return
        # Check that new keybind isn't already in use
        if CardCatManager.contains_keybind(new_keybind):
            UpdateLabel.report(f"'{keybind}' already being used for {CardCatManager.keys_and_cats[keybind].name} :c")
            return

        CardCatManager.update_keybind(new_keybind, self)
        self.keybind = new_keybind
        self.set_header_name()
#----------------------------------------------------------------------------------------------------#
    def rename(self):
        # Open pop-up to rename the specified label
        new_name = simpledialog.askstring(
            "Rename", 
            "Enter new name:",
            initialvalue=self.name,
            parent=self.winfo_toplevel()
        )
        # If no new name is given, exit 
        if not new_name:
            return
        # If new name is empty, yell at user
        if len(new_name) == 0:
            UpdateLabel.report("Name cannot be empty :S")
            return
        # Check that new name isn't already in use
        if CardCatManager.contains_cat_name(new_name):
            UpdateLabel.report(f"'{name}' already being used :c")
            return

        CardCatManager.update_cat_name(new_name, self)
#----------------------------------------------------------------------------------------------------#
    def show_menu(self):
        menu_x_pos = self.menu_button.winfo_rootx()
        menu_y_pos = self.menu_button.winfo_rooty() + self.menu_button.winfo_height()
        self.menu.post(menu_x_pos, menu_y_pos)
#----------------------------------------------------------------------------------------------------#
    # Return the number of total cards in this category
    def size(self):
        if self.local_cards_df.shape[0] == 0:
            return 0
        return self.local_cards_df['count'].sum()

    def _row_name_template(self, card_row):
        is_primary = card_row['main_category'] == self.name
        primary_is_relevant = len(card_row['all_categories']) > 1

        # Only add primary marker if it needs to be clarified
        if CardCatManager.primary_only:
            primary_marker = ''
        else:
            primary_marker = '*' if is_primary and primary_is_relevant else ''

        if card_row['count'] > 1:
            return f"{card_row.name} x{card_row['count']} {primary_marker}" 
        else:
            return f"{card_row.name} {primary_marker}"
#----------------------------------------------------------------------------------------------------#
    # Reloads the items in the listbox so they match the internal DataFrame DB
    def fill_listbox(self):
        if self.local_cards_df.shape[0] == 0:
            return
        # If we're only displaying in primary category, then just show the names and counts normally
        if CardCatManager.primary_only:
            card_rows_to_show = self.local_cards_df[self.local_cards_df['main_category'] == self.name]
        # Otherwise, show all cards as normal
        else:
            card_rows_to_show = self.local_cards_df

        new_names_series = card_rows_to_show.apply(lambda card_row: self._row_name_template(card_row), axis=1)
        # If the DataFrame is empty, then it will be a DataFrame, otherwise will be a Series
        if type(new_names_series) == pd.DataFrame:
            return
        
        # Add all names from the list
        names_list = new_names_series.to_list()
        for new_name in names_list:
            self.listbox.insert(tk.END, new_name)

        # Auto-grow/contract the listbox height
        item_count = self.listbox.size()
        new_size = max(self.min_height, item_count)
        self.listbox.config(height=new_size)
#----------------------------------------------------------------------------------------------------#
    # Returns the currently selected index 
    # If nothing is selected, returns None
    def selected_index(self):
        selected_indices = self.listbox.curselection()
        if not selected_indices:
            return None
        return selected_indices[0]
#----------------------------------------------------------------------------------------------------#
    # Returns the currently selected row as a Series
    # If no row is selected, returns None
    def selected_row(self):
        selected_index = self.selected_index()
        if selected_index is None:
            return None
        selected_row_series = self.local_cards_df.iloc[selected_index]
        return selected_row_series
#----------------------------------------------------------------------------------------------------#
    def goto(self, index):
        self.listbox.focus_set()
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(index)
        self.listbox.activate(index)
#----------------------------------------------------------------------------------------------------#
    def focus(self, card_name):
        card_index = self.local_cards_df.index.get_loc(card_name)
        self.goto(card_index)
#----------------------------------------------------------------------------------------------------#
    def _update_count(self, difference):
        print(f"updating by {difference}")
        target_idx = self.selected_index()
        target_card_name = self.local_cards_df.index[target_idx]

        new_count = self.local_cards_df.loc[target_card_name, 'count'] + difference
        # If we remove more cards than there are, then remove that card everywhere
        if new_count <= 0:
            CardCatManager.delete_card(target_card_name)
        # Otherwise, just need to update its count
        else:
            CardCatManager._update_count(target_card_name, difference, self.name)
#----------------------------------------------------------------------------------------------------#
    def add(self):
        self._update_count(1)
#----------------------------------------------------------------------------------------------------#
    def add_5(self):
        self._update_count(5)
#----------------------------------------------------------------------------------------------------#
    def subtract(self):
        self._update_count(-1)
#----------------------------------------------------------------------------------------------------#
    def subtract_5(self):
        self._update_count(-5)
#----------------------------------------------------------------------------------------------------#
    # Deletes a card row based on its name from the local df and central df
    def delete(self, card_name):
        CardCatManager.remove_card_from_cat(self, card_name)
#----------------------------------------------------------------------------------------------------#
    # Deletes the currently selected card from the local df and central df
    def delete_selected_row(self, event=None):
        selected_row = self.selected_row()
        if selected_row is None:
            return
        selected_card_name = selected_row.name
        self.delete(selected_card_name)
#----------------------------------------------------------------------------------------------------#
    # Confirms with user if they wish to delete this category
    def ask_to_delete(self):
        if messagebox.askyesno("Delete", f"Delete {self.header_name}?", icon='question'):
            CardCatManager.delete_category(self)