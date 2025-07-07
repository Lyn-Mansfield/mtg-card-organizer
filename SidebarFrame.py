import tkinter as tk
from tkinter import ttk

class SidebarFrame(tk.Frame):
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
        self.sort_options_title_label.pack(side=tk.TOP, padx=5, pady=5)
        
        self.cat_sort_label = tk.Label(
            self.centered_frame,
            text='Category Sort:'
        )
        self.cat_sort_label.pack(side=tk.TOP, padx=5, pady=5)

        default_cat_sort_option = 'Alphabetical'
        cat_sort_options = ['Alphabetical', 'Size', 'Type', 'Color']
        
        self.target_cat_sort = tk.StringVar(value='Alphabetical')
        self.cat_sort_options_menu = ttk.OptionMenu(
            self.centered_frame, self.target_cat_sort, default_cat_sort_option, *cat_sort_options
        )
        self.cat_sort_options_menu.pack(side=tk.TOP)
        self.cat_sort_options_menu.config(width=9)

        self.block_sort_label = tk.Label(
            self.centered_frame,
            text='Block Sort:'
        )
        self.block_sort_label.pack(side=tk.TOP, padx=5, pady=5)

        default_block_sort_option = 'Alphabetical'
        block_sort_options = ['Alphabetical', 'Date Added', 'Number', 'Color', 'Power', 'Toughness']
        
        self.target_block_sort = tk.StringVar(value='Alphabetical')
        self.block_sort_options_menu = ttk.OptionMenu(
            self.centered_frame, 
            self.target_block_sort, 
            default_block_sort_option, 
            *block_sort_options,
        )
        self.block_sort_options_menu.pack(side=tk.TOP)
        self.block_sort_options_menu.config(width=9)