import tkinter as tk
import pandas as pd
from tkinter import messagebox
from tkinter import simpledialog
from UpdateLabel import UpdateLabel
from CardDB import CardDB
from CardDisplayFrame import CardDisplayFrame

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
        self.menu.add_command(label="Delete", command=self.ask_to_delete)

        # Cards listbox
        self.listbox = tk.Listbox(
            self,
            height=self.min_height
        )
        self.listbox.pack(side=tk.TOP, expand=True, fill=tk.X)

        # Bind transfer command
        self.delete_command = delete_command
        self.listbox.bind('<<ListboxSelect>>', lambda event: self._on_select(event))
        self.listbox.bind('<Key>', lambda event: self._on_keystroke(event))

        # Initialize local_cards_df if no previous data exists
        self.local_cards_df = pd.DataFrame() if data is None else data

        self.update_listbox()
#----------------------------------------------------------------------------------------------------#
    def _on_select(self, event):
        selected_row = self.selected_row()
        # If there's nothing to display, then display nothing
        if selected_row is None:
            CardDisplayFrame.clear_all()
            return
        selected_image_link = selected_row['image_uris.png'].iloc[0]
        CardDisplayFrame.display_new_image(selected_image_link)
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
                CardDB.transfer_card(self, event.char)
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
        if CardDB.contains_keybind(new_keybind):
            UpdateLabel.report(f"'{keybind}' already being used for {CardDB.keys_and_cats[keybind].name} :c")
            return

        CardDB.update_keybind(self.keybind, new_keybind, self)
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
        if CardDB.contains_cat_name(new_name):
            UpdateLabel.report(f"'{name}' already being used :c")
            return

        CardDB.update_cat_name(self.name, new_name, self)
        self.name = new_name
        self.set_header_name()
#----------------------------------------------------------------------------------------------------#
    def show_menu(self):
        menu_x_pos = self.menu_button.winfo_rootx()
        menu_y_pos = self.menu_button.winfo_rooty() + self.menu_button.winfo_height()
        self.menu.post(menu_x_pos, menu_y_pos)
#----------------------------------------------------------------------------------------------------#
    # Make a copy of this category attached to a new root
    def copy(self, new_root=None):
        if new_root is None:
            new_root = self.root

        cat_block_clone = CategoryBlock(
            new_root, 
            self.keybind,
            self.name, 
            self.delete_command,
            data=self.local_cards_df.copy()
        )
        return cat_block_clone
#----------------------------------------------------------------------------------------------------#
    # Return the number of total cards in this category
    def size(self):
        if self.local_cards_df.shape[0] == 0:
            return 0
        return self.local_cards_df['count'].sum()
#----------------------------------------------------------------------------------------------------#
    # Reloads the items in the listbox so they match the internal DataFrame DB
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
    # Returns the currently selected index 
    # If nothing is selected, returns None
    def selected_index(self):
        selected_indices = self.listbox.curselection()
        if not selected_indices:
            return None
        return selected_indices[0]
#----------------------------------------------------------------------------------------------------#
    # Returns the currently selected row as a DataFrame copy
    # If no row is selected, returns None
    def selected_row(self):
        selected_index = self.selected_index()
        if selected_index is None:
            return None
        selected_row_series = self.local_cards_df.iloc[selected_index]
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
        CardDB.add_card(self, new_item_row)
        self.update_listbox()
#----------------------------------------------------------------------------------------------------#
    def update_count(self, difference):
        print(f"updating by {difference}")
        target_idx = self.selected_index()
        target_card_name = self.local_cards_df.index[target_idx]
        # Automatically updates the central DB since they share row references
        self.local_cards_df.loc[target_card_name, 'count'] += difference
        CardDB._update_sizes()

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
    # Deletes a card row from the local df and central df
    def delete(self, card_name):
        self.local_cards_df.drop(card_name, inplace=True)
        CardDB.delete_card(self, card_name)

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