import tkinter as tk
from tkinter import messagebox

class CategoryBlock:
    # Category block configuration
    min_width = 250
    min_height = 6
    block_padding = 5
#----------------------------------------------------------------------------------------------------#
    def __init__(self, root, keybind, name, keystroke_command, delete_command, data=None):
        if not (isinstance(keybind, str) and isinstance(name, str)): 
            raise TypeError("keybind and name must be strings")
        if data is not None and hasattr(data, '__iter__') == False: 
            raise TypeError("data must be iterable")

        self.root = root
        self.whole_frame = tk.Frame(
            self.root,
            height=300,
            width=self.min_width,
            highlightbackground='blue',
            highlightthickness=1
        )

        self.top_frame = tk.Frame(self.whole_frame)
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

        self.menu = tk.Menu(self.whole_frame, tearoff=0)
        self.menu.add_command(label="Option 1", command=lambda: self.menu_action(1))
        self.menu.add_command(label="Option 2", command=lambda: self.menu_action(2))
        self.menu.add_separator()
        self.menu.add_command(label="Delete", command=self.ask_to_delete)

        # Cards listbox
        self.listbox = tk.Listbox(
            self.whole_frame,
            height=self.min_height
        )
        if data is not None:
            for item in data:
                self.add(item)
        self.listbox.pack(side=tk.TOP, expand=True, fill=tk.X)

        # Bind transfer command
        self.keystroke_command = keystroke_command
        self.delete_command = delete_command
        self.listbox.bind('<Key>', lambda event: self.keystroke_command(self, event))
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
            data=self.listbox.get(0, tk.END)
        )
        return cat_block_clone
#----------------------------------------------------------------------------------------------------#
    def size(self):
        return self.listbox.size()
#----------------------------------------------------------------------------------------------------#
    def resize(self):
        # Auto-grow/contract the listbox height
        item_count = self.listbox.size()
        new_size = max(self.min_height, item_count)
        self.listbox.config(height=new_size)
#----------------------------------------------------------------------------------------------------#
    def curselection(self):
        return self.listbox.curselection()
#----------------------------------------------------------------------------------------------------#
    def get(self, index):
        return self.listbox.get(index)
#----------------------------------------------------------------------------------------------------#
    def add(self, new_item):
        self.listbox.insert(tk.END, new_item)
        self.resize()
#----------------------------------------------------------------------------------------------------#
    def delete(self, index):
        self.listbox.delete(index)
        self.resize()
#----------------------------------------------------------------------------------------------------#
    def delete_selected_entry(self, event=None):
        print('trying to delete!')
        selected_index = self.listbox.curselection()
        self.delete(selected_index)
#----------------------------------------------------------------------------------------------------#
    def pack(self, side=None, padx=None, pady=None, expand=False, fill=None):
        if padx is None:
            padx = self.block_padding
        if pady is None:
            pady = self.block_padding
        self.whole_frame.pack(side=side, padx=padx, pady=pady, expand=expand, fill=fill)
#----------------------------------------------------------------------------------------------------#
    def pack_forget(self):
        self.whole_frame.pack_forget()
#----------------------------------------------------------------------------------------------------#
    def ask_to_delete(self):
        if messagebox.askyesno("Delete", f"Delete {self.header_name}?", icon='question'):
            self.delete_command(self.name)
#----------------------------------------------------------------------------------------------------#
    def destroy(self):
        self.whole_frame.destroy()
