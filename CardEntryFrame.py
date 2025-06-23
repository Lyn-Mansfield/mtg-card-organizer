import tkinter as tk
from tkinter import ttk

class CardEntryFrame:
    def __init__(self, root, add_item_command=None, add_cat_command=None, highlightbackground=None, highlightthickness=None):
        # Whole frame, thing everything is inside of
        self.whole_frame = tk.Frame(
            root, 
            highlightbackground=highlightbackground, 
            highlightthickness=highlightthickness
        )

        # Search frame
        self.search_frame = tk.Frame(
            self.whole_frame, 
            highlightbackground='brown', 
            highlightthickness=2
        )
        self.search_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=10, pady=5)

        # Card entry
        self.card_entry = ttk.Entry(self.search_frame)
        self.card_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        self.card_entry.bind('<Return>', add_item_command)

        # Category Selection Menu
        self.target_category = tk.StringVar(value="Unsorted")
        self.category_selector = ttk.OptionMenu(
            self.search_frame, self.target_category, *[], command=lambda _: self.card_entry.focus()
        )
        self.category_selector.pack(side=tk.LEFT, padx=(0, 5))

        # Custom category frame
        self.add_cat_frame = tk.Frame(
            self.whole_frame, 
            highlightbackground='silver', 
            highlightthickness=2
        )
        self.add_cat_frame.pack(side=tk.LEFT, fill=tk.X)

        # Custom category entry
        one_char_validation = (self.whole_frame.register(self._validate_one_char), '%P')
        self.keybind_entry = tk.Entry(
            self.add_cat_frame, 
            width=1,
            validate="key", 
            validatecommand=one_char_validation
        )
        self.keybind_entry.pack(side=tk.LEFT)

        self.cat_name_entry = tk.Entry(self.add_cat_frame)
        self.cat_name_entry.pack(side=tk.LEFT)
        self.cat_name_entry.bind('<Return>', add_cat_command)

        self.add_button = ttk.Button(
            self.add_cat_frame, text="Add", command=add_cat_command
        )
        self.add_button.pack(side=tk.LEFT)

    def _validate_one_char(self, P):
        if len(P) <= 1:
            return True
        else:
            return False

    def pack(self, side=None, padx=None, pady=None, expand=False, fill=None):
        self.whole_frame.pack(side=side, padx=padx, pady=pady, expand=expand, fill=fill)

    def get_curr_category(self):
        return self.target_category.get()

    def output_card_entry(self):
        card_name = self.card_entry.get()
        self.card_entry.delete(0, tk.END)
        return card_name

    def output_new_cat_entries(self):
        keybind = self.keybind_entry.get().strip()
        name = self.cat_name_entry.get().strip()
        if len(keybind) == 0 or len(name) == 0:
            raise Exception("No input for keybind and/or name")

        self.keybind_entry.delete(0, tk.END)
        self.cat_name_entry.delete(0, tk.END)
        return (keybind, name)

    # Add defaults of None so that we can pass in defaults without any input 
    # in the custom category entry boxes
    def add_category(self, keybind=None, name=None):
        # If not a default category, then both will be None
        if keybind is None and name is None:
            keybind, name = self.get_new_cat_info()

        # Update drop-down menu
        self.category_selector['menu'].add_command(
            label=name, 
            command=tk._setit(self.target_category, name)
        )