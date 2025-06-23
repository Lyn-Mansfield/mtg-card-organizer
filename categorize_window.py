import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk
from CardEntryFrame import CardEntryFrame

class CategoryBlockFrame:
    def __init__(self, root, highlightbackground=None, highlightthickness=None):
        # Category/Keybind storage
        self.cat_frames = {}
        self.key_bindings = {}

        # Whole frame, where everything lives
        self.whole_frame = tk.Frame(
            root, 
            highlightbackground=highlightbackground, 
            highlightthickness=highlightthickness
        )
        self.whole_frame.bind('<Configure>', self.on_window_resize)

        # Category canvas to house scrollbar
        self.categories_canvas = tk.Canvas(
            self.whole_frame,
            highlightbackground='black',
            highlightthickness=4
        )
        self.categories_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = ttk.Scrollbar(
            self.categories_canvas, 
            orient=tk.VERTICAL, 
            command=self.categories_canvas.yview
        )
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.categories_canvas.configure(yscrollcommand=self.scrollbar.set)

        # Inner category frame for category blocks
        self.categories_frame = tk.Frame(
            self.categories_canvas,
            highlightbackground='green',
            highlightthickness=4
        )
        self.categories_canvas.create_window(
            (0, 0), 
            window=self.categories_frame, 
            anchor="nw",
            tags=("inner_frame",)
        )
        self.categories_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Category block configuration
        self.min_cat_frame_width = 300
        self.min_listbox_height = 10
        self.block_padding = 5

    def _on_mousewheel(self, event):
        """Handle mousewheel only when scrolling is needed"""
        categories_frame_height = self.categories_frame.winfo_reqheight()
        categories_canvas_height = self.categories_canvas.winfo_height()
        if categories_frame_height > categories_canvas_height:
            self.categories_canvas.yview_scroll(-1 * event.delta, "units")

    def _transfer_card(self, curr_listbox, event):
        """Handle key presses for moving cards from category to category"""
        if curr_listbox.size() == 0:
            return
        selected_index = curr_listbox.curselection()
        selected_card = curr_listbox.get(selected_index[0])
        
        keybind = event.char
        if keybind not in self.key_bindings.keys():
            return
        target_category_name = self.key_bindings[keybind]
        target_listbox = self.cat_frames[target_category_name].listbox

        # Remove from current category, transfer to new category
        curr_listbox.delete(selected_index)
        target_listbox.insert(tk.END, selected_card)

    def pack(self, side=None, padx=None, pady=None, expand=False, fill=None):
        self.whole_frame.pack(side=side, padx=padx, pady=pady, expand=expand, fill=fill)

    def add_category(self, keybind, name):
        print("adding new category block!")
        new_cat_frame = tk.Frame(
            self.categories_frame,
            height=300,
            width=self.min_cat_frame_width,
            highlightbackground='blue',
            highlightthickness=1
        )
        new_cat_frame.label = tk.Label(new_cat_frame, text=f'{name} ({keybind})')
        new_cat_frame.label.pack(side=tk.TOP)
        new_cat_frame.listbox = tk.Listbox(
            new_cat_frame,
            height=self.min_listbox_height
        )
        new_cat_frame.listbox.pack(side=tk.TOP, expand=True, fill=tk.X)
        new_cat_frame.listbox.bind('<Key>', lambda event: self._transfer_card(new_cat_frame.listbox, event))
        
        # Update dictionaries
        self.cat_frames[name] = new_cat_frame
        self.key_bindings[keybind] = name

        # Reorganize the blocks
        self.reorganize_listboxes()

    def reorganize_listboxes(self):
        print(self.categories_canvas.bbox("all"))
        print(self.categories_canvas.winfo_width())
        """Calculate optimal columns and reposition listbox frames"""
        cat_frames = self.cat_frames.values()
        
        # Calculate available columns
        canvas_width = self.categories_canvas.winfo_width()
        max_columns = max(1, canvas_width // self.min_cat_frame_width)
        columns = min(max_columns, len(self.cat_frames))
        
        # Reset all column weights
        for col in range(self.categories_frame.grid_size()[0]):
            self.categories_frame.columnconfigure(col, weight=0)

        # Repack listboxes in grid layout
        for i, cat_frame in enumerate(cat_frames):
            print(cat_frame.label.cget("text"))
            row = i // columns
            col = i % columns
            cat_frame.grid(
                row=row, 
                column=col, 
                padx=self.block_padding, 
                pady=self.block_padding, 
                sticky="nsew"
            )
        
        # Readd grid weights to fill the extra space
        for col in range(columns):
            self.categories_frame.columnconfigure(col, weight=1)

        # Resize inner frame to take up available space
        new_inner_width = self.categories_canvas.winfo_width() - 20
        self.categories_canvas.itemconfigure("inner_frame", width=new_inner_width)

    def add_new_item(self, new_item, target_category):
        print("trying to add new item!")
        """Add an item to the selected listbox"""
        target_listbox = self.cat_frames[target_category].listbox
        target_listbox.insert(tk.END, new_item)
        
        # Auto-grow the listbox height
        item_count = target_listbox.size()
        new_size = max(self.min_listbox_height, item_count)
        target_listbox.config(height=new_size)

    def on_window_resize(self, event):
        # Leave some space for the scrollbar
        new_inner_width = self.categories_canvas.winfo_width() - 20
        self.categories_canvas.itemconfigure("inner_frame", width=new_inner_width)
        
        # Update scrollregion (full height, current width)
        self.categories_canvas.configure(scrollregion=self.categories_canvas.bbox("inner_frame"))

        # Have category blocks fill in the new space
        self.reorganize_listboxes()




class MultiColumnListboxApp:
    def __init__(self, root):
        # Root setup
        self.root = root
        self.root.geometry("800x600")
        self.root.title("MTG Deck Column Organizer")

        # Sidebar frame
        self.sidebar_frame = tk.Frame(root, width=100, highlightbackground='yellow', highlightthickness=4)
        self.sidebar_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)

        # Sort options frame
        self.sort_options_frame = tk.Frame(self.sidebar_frame)
        self.sort_options_frame.pack(expand=True)
        
        self.sort_options_title_label = tk.Label(
            self.sort_options_frame, 
            text='Sort Options',
            font=('Arial', 16, 'underline')
        )
        self.sort_options_title_label.pack(side=tk.TOP, padx=5, pady=5)
        
        self.cat_sort_label = tk.Label(
            self.sort_options_frame,
            text='Category Sort:'
        )
        self.cat_sort_label.pack(side=tk.TOP, padx=5, pady=5)
        default_cat_sort_option = 'Alphabetical'
        cat_sort_options = ['Alphabetical', 'Size', 'Type', 'Color']
        
        self.target_cat_sort = tk.StringVar(value='Alphabetical')
        self.cat_sort_options_menu = ttk.OptionMenu(
            self.sort_options_frame, self.target_cat_sort, default_cat_sort_option, *cat_sort_options
        )
        self.cat_sort_options_menu.pack(side=tk.TOP)

        self.block_sort_label = tk.Label(
            self.sort_options_frame,
            text='Block Sort:'
        )
        self.block_sort_label.pack(side=tk.TOP, padx=5, pady=5)
        default_block_sort_option = 'Alphabetical'
        block_sort_options = ['Alphabetical', 'Date Added', 'Number', 'Color', 'Power', 'Toughness']
        
        self.target_block_sort = tk.StringVar(value='Alphabetical')
        self.block_sort_options_menu = ttk.OptionMenu(
            self.sort_options_frame, 
            self.target_block_sort, 
            default_block_sort_option, 
            *block_sort_options
        )
        self.block_sort_options_menu.pack(side=tk.TOP)


        # Body frame
        self.body_frame = tk.Frame(root, highlightbackground='red', highlightthickness=4)
        self.body_frame.pack(side=tk.LEFT, padx=10, pady=10, expand=True, fill=tk.BOTH)

        # Input frame
        self.input_frame = CardEntryFrame(
            self.body_frame, 
            add_item_command=self.add_new_item, 
            add_cat_command=self.add_custom_category, 
            highlightbackground='white', 
            highlightthickness=3
        )
        self.input_frame.pack(side=tk.TOP, fill=tk.X)

        # Block frame
        self.block_frame = CategoryBlockFrame(
            self.body_frame,
            highlightbackground='black', 
            highlightthickness=3
        )
        self.block_frame.pack(padx=10, pady=(0, 10), expand=True, fill=tk.BOTH)


        # Initial setup
        default_categories = {
            'u': "Unsorted",
            'c': "Card Draw",
            'p': "Protection",
            't': "Tutor",
            's': "Sac Outlet",
            'm': "Mana Ramp",
            'l': "Land"
        }
        for (keybind, name) in default_categories.items():
            self.add_category(keybind, name)
        # Bind window resize event

    def add_category(self, keybind, name):
        # Add category to options menu
        self.input_frame.add_category(keybind=keybind, name=name)

        # Add a new category block
        self.block_frame.add_category(keybind, name)

    def add_custom_category(self, event):
        # Get custom category information
        try:
            (keybind, name) = self.input_frame.output_new_cat_entries()
        except Exception as e:
            return

        self.add_category(keybind, name)
    
    def add_new_item(self, event):
        print("trying to add new item!")
        """Add an item to the selected listbox"""
        target_category = self.input_frame.get_curr_category()
        new_item = self.input_frame.output_card_entry()

        if len(new_item) == 0:
            return
        self.block_frame.add_new_item(new_item, target_category)


root = tk.Tk()
app = MultiColumnListboxApp(root)
root.mainloop()