import tkinter as tk
import pandas as pd
from tkinter import messagebox
from UpdateLabel import UpdateLabel
from CardDB import CardDB

class CategoryBlock(tk.Frame):
    # Category block configuration
    min_width = 210
    min_height = 6
#----------------------------------------------------------------------------------------------------#
    def __init__(self, root, keybind, name, delete_command, data=None):
        if not (isinstance(keybind, str) and isinstance(name, str)): 
            raise TypeError("keybind and name must be strings")
        if data is not None and hasattr(data, '__iter__') == False: 
            raise TypeError("data must be iterable")

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
        self.header_name = f"{name} ({keybind})"
        self.header = tk.Label(
            self.top_frame, 
            text=self.header_name
        )
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
        self.menu.add_command(label="Print central DB", command=self.print_central_db)
        self.menu.add_command(label="Print instance DB", command=self.print_db)
        self.menu.add_separator()
        self.menu.add_command(label="Delete", command=self.ask_to_delete)

        # Cards listbox
        self.listbox = tk.Listbox(
            self,
            height=self.min_height
        )
        self.listbox.pack(side=tk.TOP, expand=True, fill=tk.X)

        # Bind transfer command
        self.delete_command = delete_command
        self.listbox.bind('<Key>', lambda event: self._on_keystroke(event))

        # Initialize local_cards_df if no previous data exists
        self.local_cards_df = pd.DataFrame() if data is None else data
        if name == 'Unsorted':
            print(name, self.local_cards_df)
        self.update_listbox()
#----------------------------------------------------------------------------------------------------#
    def _on_keystroke(self, event):
        """Handle key presses for moving cards from category to category"""
        print('generic keystroke detected...')
        print(event.keysym)

        match event.keysym:
            case "BackSpace" | "Delete":
                self.delete_selected_entry()
            case "equal":
                self.add()
            case "plus":
                self.add_5()
            case "minus":
                self.subtract()
            case "underscore":
                self.subtract_5()
            case _:
                print("|=================|")
                print("!Transferring Card!")
                print("|=================|")
                CardDB.transfer(self, event.char)
#----------------------------------------------------------------------------------------------------#
    def print_central_db(self):
        print(f"Central DB:")
        print(CardDB.cards_df['count'])
#----------------------------------------------------------------------------------------------------#
    def print_db(self):
        print(f"{self.name} Category's DB:")
        print(self.local_cards_df)
#----------------------------------------------------------------------------------------------------#
    def show_menu(self):
        menu_x_pos = self.menu_button.winfo_rootx()
        menu_y_pos = self.menu_button.winfo_rooty() + self.menu_button.winfo_height()
        self.menu.post(menu_x_pos, menu_y_pos)
#----------------------------------------------------------------------------------------------------#
    def copy(self, new_root=None):
        if new_root is None:
            new_root = self.root

        # Add a copy of local_cards_df to dereference it from the old one
        cat_block_clone = CategoryBlock(
            new_root, 
            self.keybind,
            self.name, 
            self.delete_command,
            data=self.local_cards_df.copy()
        )
        return cat_block_clone
#----------------------------------------------------------------------------------------------------#
    def size(self):
        return self.listbox.size()
#----------------------------------------------------------------------------------------------------#
    def update_listbox(self):
        new_names_series = self.local_cards_df.apply(lambda row: f"{row.name} x{row['count']}" if row['count'] > 1 else row.name, axis=1)
        # If the DataFrame is empty, then it will be a DataFrame, otherwise will be a Series
        if type(new_names_series) == pd.DataFrame:
            return
        names_list = new_names_series.to_list()
        
        # Wipe all names, then re-add them
        self.listbox.delete(0, tk.END)
        for new_name in names_list:
            self.listbox.insert(tk.END, new_name)

        # Auto-grow/contract the listbox height
        item_count = self.listbox.size()
        new_size = max(self.min_height, item_count)
        self.listbox.config(height=new_size)
#----------------------------------------------------------------------------------------------------#
    # returns the currently selected index
    def selected_index(self):
        return self.listbox.curselection()[0]
#----------------------------------------------------------------------------------------------------#
    # returns the currently selected row as a DataFrame copy
    def selected_row(self):
        selected_row_series = self.local_cards_df.iloc[self.selected_index()]
        return selected_row_series.to_frame().T
#----------------------------------------------------------------------------------------------------#
    def get(self, index):
        return self.listbox.get(index)
#----------------------------------------------------------------------------------------------------#
    def goto(self, index):
        self.listbox.focus_set()
        self.listbox.selection_set(index)
#----------------------------------------------------------------------------------------------------#
    def insert(self, new_item_row):
        self.local_cards_df = pd.concat([self.local_cards_df, new_item_row])
        new_item_row['main_category'] = [self]
        CardDB.add(new_item_row)
        self.update_listbox()
#----------------------------------------------------------------------------------------------------#
    # Automatically updates the Card DB since self.local_cards_df references the same row in CardDB
    def update_count(self, difference):
        print(f"updating by {difference}")
        target_idx = self.selected_index()
        target_card_name = self.local_cards_df.index[target_idx]
        self.local_cards_df.loc[target_card_name, 'count'] += difference

        new_count = self.local_cards_df.loc[target_card_name, 'count']
        if new_count <= 0:
            self.delete(target_card_name)

        self.update_listbox()
        self.goto(target_idx)
#----------------------------------------------------------------------------------------------------#
    def add(self):
        self.update_count(1)
#----------------------------------------------------------------------------------------------------#
    def add_5(self):
        self.update_count(5)
#----------------------------------------------------------------------------------------------------#
    def subtract(self):
        self.update_count(-1)
#----------------------------------------------------------------------------------------------------#
    def subtract_5(self):
        self.update_count(-5)
#----------------------------------------------------------------------------------------------------#
    def delete(self, card_name):
        self.local_cards_df.drop(card_name, inplace=True)
        CardDB.delete(card_name)

        UpdateLabel.report(f"Deleted {card_name} from {self.name}")
        self.update_listbox()
#----------------------------------------------------------------------------------------------------#
    def delete_selected_entry(self, event=None):
        try:
            selected_index = self.listbox.curselection()
        except:
            UpdateLabel.report("Nothing to delete :S")
            return
        selected_card_name = self.local_cards_df.index[selected_index]
        self.delete(selected_card_name)
#----------------------------------------------------------------------------------------------------#
    def ask_to_delete(self):
        if messagebox.askyesno("Delete", f"Delete {self.header_name}?", icon='question'):
            self.delete_command(self.name)