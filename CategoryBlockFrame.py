import tkinter as tk
from tkinter import ttk

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
        self.categories_canvas.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

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
        self.min_cat_frame_width = 250
        self.min_listbox_height = 10
        self.block_padding = 5

    def _on_mousewheel(self, event):
        # Handle mousewheel only when scrolling makes sense
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
            row = i // columns
            col = i % columns
            cat_frame.grid(
                row=row, 
                column=col, 
                padx=self.block_padding, 
                pady=self.block_padding, 
                sticky="ew"
            )
        
        # Readd grid weights to fill the extra space
        for col in range(columns):
            self.categories_frame.columnconfigure(col, weight=1)

    def add_new_item(self, new_item, target_category):
        target_listbox = self.cat_frames[target_category].listbox
        target_listbox.insert(tk.END, new_item)
        
        # Auto-grow the listbox height
        item_count = target_listbox.size()
        new_size = max(self.min_listbox_height, item_count)
        target_listbox.config(height=new_size)

    def on_window_resize(self, event):
        # Add this to avoid timing issues with canvas not growing correctly
        self.whole_frame.update_idletasks()

        # Leave some space for the scrollbar
        new_inner_width = self.categories_canvas.winfo_width() - self.scrollbar.winfo_width()
        self.categories_canvas.itemconfigure("inner_frame", width=new_inner_width)
        
        # Have category blocks fill in the new space
        self.reorganize_listboxes()

        # Update scrollregion
        self.categories_frame.update_idletasks()
        self.categories_canvas.configure(scrollregion=self.categories_canvas.bbox("inner_frame"))


