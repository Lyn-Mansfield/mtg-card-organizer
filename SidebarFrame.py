import tkinter as tk
from tkinter import ttk

class SidebarFrame(tk.Frame):
    default_cat_sort_option = 'Alphabetical'
    default_block_sort_option = 'Alphabetical'

    def __init__(self, root, **kwargs):
        # Everything lives in self
        super().__init__(root, **kwargs)
        # Instantiate the class StringVars after making the frame they live in
        self._class_init()
        
        # Centered frame, since we want everything in the middle
        self.centered_frame = tk.Frame(self)
        self.centered_frame.pack(expand=True)
        
        self.sort_options_title_label = tk.Label(
            self.centered_frame, 
            text='Sort Options',
            font=('Arial', 16, 'underline')
        )
        self.sort_options_title_label.pack(side=tk.TOP, padx=5, pady=5)
        
        self.cat_sort_label = tk.Label(
            self.centered_frame,
            text='Category Sort:'
        )
        self.cat_sort_label.pack(side=tk.TOP, padx=5, pady=5)

        options_menu_width = 9
        # WIP: Add way of broadcasting to CardDB whenever a new option is chosen
        cat_sort_options = ['Alphabetical', 'Size', 'Type', 'Color']
        self.cat_order_options_menu = ttk.OptionMenu(
            self.centered_frame, 
            self.cat_order, 
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

        block_sort_options = ['Alphabetical', 'Date Added', 'Number', 'Color', 'Power', 'Toughness']
        self.block_order_options_menu = ttk.OptionMenu(
            self.centered_frame, 
            self.block_order, 
            self.default_block_sort_option, 
            *block_sort_options
        )
        self.block_order_options_menu.pack(side=tk.TOP)
        self.block_order_options_menu.config(width=options_menu_width)


    @classmethod
    def _class_init(cls):
        cls.cat_order = tk.StringVar(value=cls.default_cat_sort_option)
        cls.block_order = tk.StringVar(value=cls.default_block_sort_option)


    @classmethod
    def cat_order(cls):
        return cls.cat_order.get()
    
    @classmethod
    def block_order(cls):
        return cls.cat_order.get()

