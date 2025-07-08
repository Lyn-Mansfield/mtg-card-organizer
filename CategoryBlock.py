import tkinter as tk
import pandas as pd
from tkinter import messagebox
from UpdateLabel import UpdateLabel

class CategoryBlock(tk.Frame):
    # Category block configuration
    min_width = 210
    min_height = 6
#----------------------------------------------------------------------------------------------------#
    def __init__(self, root, keybind, name, keystroke_command, delete_command, data=None):
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
        self.menu.add_command(label="Option 1", command=lambda: self.menu_action(1))
        self.menu.add_command(label="Option 2", command=lambda: self.menu_action(2))
        self.menu.add_separator()
        self.menu.add_command(label="Delete", command=self.ask_to_delete)

        # Cards listbox
        self.listbox = tk.Listbox(
            self,
            height=self.min_height
        )
        self.listbox.pack(side=tk.TOP, expand=True, fill=tk.X)

        # Bind transfer command
        self.keystroke_command = keystroke_command
        self.delete_command = delete_command
        self.listbox.bind('<Key>', lambda event: self.keystroke_command(self, event))

        self.items_df = pd.DataFrame() if data is None else data
        self.update_listbox()
#----------------------------------------------------------------------------------------------------#
    def show_menu(self):
        menu_x_pos = self.menu_button.winfo_rootx()
        menu_y_pos = self.menu_button.winfo_rooty() + self.menu_button.winfo_height()
        self.menu.post(menu_x_pos, menu_y_pos)
#----------------------------------------------------------------------------------------------------#
    def copy(self, new_root=None):
        if new_root is None:
            new_root = self.root

        cat_block_clone = CategoryBlock(
            new_root, 
            self.keybind,
            self.name, 
            self.keystroke_command,
            self.delete_command,
            data=self.items_df
        )
        return cat_block_clone
#----------------------------------------------------------------------------------------------------#
    def size(self):
        return self.listbox.size()
#----------------------------------------------------------------------------------------------------#
    def update_listbox(self):
        new_names = self.items_df.apply(lambda row: f"{row['name']} x{row['count']}" if row['count'] > 1 else row['name'], axis=1)
        # If the DataFrame is empty, then it will be a DataFrame, otherwise will be a Series
        if type(new_names) == pd.DataFrame:
            return

        names_list = new_names.to_list()
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
    def goto(self, index):
        self.listbox.focus_set()
        self.listbox.selection_set(index)
#----------------------------------------------------------------------------------------------------#
    def get(self, index):
        return self.listbox.get(index)
#----------------------------------------------------------------------------------------------------#
    def set(self, replacement, index):
        self.listbox.delete(index)
        self.listbox.insert(index, replacement)
        self.listbox.selection_set(index)
#----------------------------------------------------------------------------------------------------#
    def insert(self, new_item_row):
        self.items_df = pd.concat([self.items_df, new_item_row])
        print(self.items_df)
        self.update_listbox()
#----------------------------------------------------------------------------------------------------#
    def _get_count(self, index):
        target_row = self.items_df.iloc[target_idx]
        return (target_row['name'], target_row['count'])
#----------------------------------------------------------------------------------------------------#
    def _set_count(self, count, index):
        self.items_df.iloc[target_idx]['count'] = count
#----------------------------------------------------------------------------------------------------#
    def add(self):
        target_idx = self.selected_index()
        count = self._get_count(target_idx)
        count += 1
        self._set_count(count, target_idx)

        self.update_listbox()
#----------------------------------------------------------------------------------------------------#
    def add_5(self):
        for _ in range(5):
            self.add()
#----------------------------------------------------------------------------------------------------#
    def subtract(self):
        target_idx = self.selected_index()
        original_name, count = self._get_name_and_count(target_idx)

        count -= 1
        self._set_count(count, target_idx)
        if count == 0:
            self.delete(target_idx)

        self.update_listbox()
#----------------------------------------------------------------------------------------------------#
    def subtract_5(self):
        target_idx = self.selected_index()
        full_target_string = self.get(target_idx)
        count = self._extract_current_count(full_target_string)

        for _ in range(min(count, 5)):
            self.subtract()
#----------------------------------------------------------------------------------------------------#
    def delete(self, index):
        self.items_df.drop(index=index)
        # Delete somehow -> self.block_frame_root.all_items_df.drop(index=index)

        UpdateLabel.report(f"Deleted {original_name} from {self.name}")
        self.update_listbox()
#----------------------------------------------------------------------------------------------------#
    def delete_selected_entry(self, event=None):
        selected_index = self.listbox.curselection()
        self.delete(selected_index)
#----------------------------------------------------------------------------------------------------#
    def ask_to_delete(self):
        if messagebox.askyesno("Delete", f"Delete {self.header_name}?", icon='question'):
            self.delete_command(self.name)
