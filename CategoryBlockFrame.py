import tkinter as tk
from tkinter import ttk
import pandas as pd
from CategoryBlock import CategoryBlock
from UpdateLabel import UpdateLabel
from CardDB import CardDB

class CategoryBlockFrame(tk.Frame):
    def __init__(self, root, delete_cat_command=None, **kwargs):
        # Everything lives in self
        super().__init__(root, **kwargs)
        self.bind('<Configure>', self.on_window_resize)

        # Category canvas to house scrollbar
        self.categories_canvas = tk.Canvas(
            self,
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

        # Category column frames list
        self.column_frames = []
        self.delete_cat_command = delete_cat_command
#----------------------------------------------------------------------------------------------------#
    def _on_mousewheel(self, event):
        # Handle mousewheel only when scrolling makes sense
        categories_frame_height = self.categories_frame.winfo_reqheight()
        categories_canvas_height = self.categories_canvas.winfo_height()
        if categories_frame_height > categories_canvas_height:
            self.categories_canvas.yview_scroll(-1 * event.delta, "units")
#----------------------------------------------------------------------------------------------------#
    def add_category(self, keybind, category_name):
        # Initialize root to the categories frame
        new_cat_block = CategoryBlock(
            self.categories_frame, 
            keybind,
            category_name, 
            self.delete_cat_command
        )
        # Update dictionaries
        CardDB.add_category(keybind, category_name, new_cat_block)
        UpdateLabel.report(f"{category_name} Category added c:")
        # Reorganize the blocks
        self.reorganize_cat_blocks()
#----------------------------------------------------------------------------------------------------#
    def delete_category(self, category_name):
        CardDB.delete_category(category_name)

        UpdateLabel.report(f"{category_name} Category deleted :S")
        self.reorganize_cat_blocks()
#----------------------------------------------------------------------------------------------------#
    def reorganize_cat_blocks(self):
        # Calculate available columns
        canvas_width = self.categories_canvas.winfo_width()
        max_columns = max(1, canvas_width // CategoryBlock.min_width)
        num_of_total_categories = len(CardDB.names_and_cats)
        new_num_of_columns = min(max_columns, num_of_total_categories)
        
        # Unpack all existing column frames
        for column_frame in self.column_frames:
            column_frame.pack_forget()

        # Add or remove frames to match how many we need
        curr_num_of_columns = len(self.column_frames)
        if curr_num_of_columns < new_num_of_columns:
            for i in range(new_num_of_columns - curr_num_of_columns):
                new_column_frame = tk.Frame(
                    self.categories_frame, 
                    highlightbackground='gray', 
                    highlightthickness=2
                )
                self.column_frames.append(new_column_frame)
        else:
            self.column_frames = self.column_frames[:new_num_of_columns]

        # Repack all column frames
        for column_frame in self.column_frames:
            column_frame.pack(side=tk.LEFT, anchor=tk.NW, expand=True, fill=tk.X)

        # Clone/repack category blocks into column frames
        i = 0
        for cat_block in CardDB.names_and_cats.values():
            column_index = i % new_num_of_columns
            i += 1
            target_column_frame = self.column_frames[column_index]

            # Clone the block frame into its new column frame
            cat_block.pack_forget()
            cat_block_clone = cat_block.copy(new_root=target_column_frame)
            cat_block_clone.pack(side=tk.TOP, expand=True, fill=tk.X)

            # Update references to clones
            CardDB._update_reference(cat_block, cat_block_clone)
            cat_block.destroy()

        # Update scrollregion
        self.categories_frame.update_idletasks()
        self.categories_canvas.update_idletasks()
        self.categories_canvas.configure(scrollregion=self.categories_canvas.bbox("inner_frame"))
#----------------------------------------------------------------------------------------------------#
    # Item rows are given as one-row DataFrames
    def add_new_item(self, new_item_row, target_category_name):
        target_cat_block_frame = CardDB.names_and_cats[target_category_name]

        new_item_name = new_item_row.index[0]
        # Catch the start case when the the df is empty
        if CardDB.contains(new_item_name):
            UpdateLabel.report(f'{new_item_name} is already added :S')
            return
            
        target_cat_block_frame.insert(new_item_row)
#----------------------------------------------------------------------------------------------------#
    def on_window_resize(self, event):
        # Add this to avoid timing issues with canvas not growing correctly
        self.update_idletasks()

        # Leave some space for the scrollbar
        new_inner_width = self.categories_canvas.winfo_width() - self.scrollbar.winfo_width()
        self.categories_canvas.itemconfigure("inner_frame", width=new_inner_width)
        
        # Have category blocks fill in the new space
        self.reorganize_cat_blocks()

