import tkinter as tk
from tkinter import ttk
from CardDB import CardDB

class SidebarFrame(tk.Frame):
    default_primary_only_option = False
    default_cat_sort_option = 'Date Added'
    default_block_sort_option = 'Alphabetical'

    def __init__(self, root, **kwargs):
        # Everything lives in self
        super().__init__(root, **kwargs)
        
        # Centered frame, since we want everything in the middle
        self.centered_frame = tk.Frame(self)
        self.centered_frame.pack(expand=True)
        
        self.sort_options_title_label = tk.Label(
            self.centered_frame, 
            text='Sort Options',
            font=('Arial', 16, 'underline')
        )

        # All listener variables are instantiated here to be used further down
        self.primary_only_bool_var = tk.BooleanVar(value=False)
        self.cat_order_string_var = tk.StringVar(value=self.default_cat_sort_option)
        self.block_order_string_var = tk.StringVar(value=self.default_block_sort_option)

        self.primary_only_bool_var.trace_add('write', self._update_class_vars)
        self.cat_order_string_var.trace_add('write', self._update_class_vars)
        self.block_order_string_var.trace_add('write', self._update_class_vars)

        self.primary_only_checkbutton = tk.Checkbutton(
            self.centered_frame, 
            text="Show in primary category only (*)", 
            variable=self.primary_only_bool_var
        )
        self.primary_only_checkbutton.pack(side=tk.TOP)

        self.sort_options_title_label.pack(side=tk.TOP, padx=5, pady=5)
        
        self.cat_sort_label = tk.Label(
            self.centered_frame,
            text='Category Sort:'
        )
        self.cat_sort_label.pack(side=tk.TOP, padx=5, pady=5)

        options_menu_width = 9
        # WIP: Add way of broadcasting to CardDB whenever a new option is chosen
        cat_sort_options = ['Date Added', 'Alphabetical', 'Size', 'Type', 'Color']
        self.cat_order_options_menu = ttk.OptionMenu(
            self.centered_frame, 
            self.cat_order_string_var, 
            self.default_cat_sort_option, 
            *cat_sort_options
        )
        self.cat_order_options_menu.pack(side=tk.TOP)
        self.cat_order_options_menu.config(width=options_menu_width)

        self.block_sort_label = tk.Label(
            self.centered_frame,
            text='Block Sort:'
        )
        self.block_sort_label.pack(side=tk.TOP, padx=5, pady=5)

        block_sort_options = ['Alphabetical', 'Mana Cost', 'Date Added', 'Number', 'Color', 'Power', 'Toughness']
        self.block_order_options_menu = ttk.OptionMenu(
            self.centered_frame, 
            self.block_order_string_var, 
            self.default_block_sort_option, 
            *block_sort_options
        )
        self.block_order_options_menu.pack(side=tk.TOP)
        self.block_order_options_menu.config(width=options_menu_width)

    # Update card DB when variables change
    # Random trace_add info gets passed in, too, but we can ignore all that
    def _update_class_vars(self, *args):
        primary_only = self.primary_only_bool_var.get()
        cat_order = self.cat_order_string_var.get()
        block_order = self.block_order_string_var.get()

        CardDB._update_class_vars(primary_only, cat_order, block_order)

