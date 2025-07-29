import tkinter as tk
from tkinter import ttk
import pandas as pd
from CategoryBlock import CategoryBlock
from UpdateLabel import UpdateLabel
from CardCatManager import CardCatManager
from CardDisplayFrame import CardDisplayFrame

class CategoryBlockFrame(tk.Frame):
    def __init__(self, root, **kwargs):
        # Everything lives in self
        super().__init__(root, **kwargs)
        self.bind('<Configure>', self.on_window_resize)
        # Register self with CardCatManager
        CardCatManager.block_frame = self

        # Category canvas to house scrollbar
        self.categories_canvas = tk.Canvas(
            self,
            highlightbackground='black',
            highlightthickness=4
        )
        self.categories_canvas.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.categories_canvas.bind('<Button-1>', lambda _: self._on_canvas_click())

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
#----------------------------------------------------------------------------------------------------#
    def _on_canvas_click(self):
        CardDisplayFrame.clear_all()
#----------------------------------------------------------------------------------------------------#
    def _on_mousewheel(self, event):
        # Handle mousewheel only when scrolling makes sense
        categories_frame_height = self.categories_frame.winfo_reqheight()
        categories_canvas_height = self.categories_canvas.winfo_height()
        if categories_frame_height > categories_canvas_height:
            self.categories_canvas.yview_scroll(-1 * event.delta, "units")
#----------------------------------------------------------------------------------------------------#
    def add_category(self, keybind, category_name):
        CardCatManager.add_category(keybind, category_name)
        UpdateLabel.report(f"{category_name} Category added c:")
        # Reorganize the blocks
        self.reorganize_cat_blocks()
#----------------------------------------------------------------------------------------------------#
    def delete_category(self, category_name):
        CardCatManager.delete_category(category_name)

        UpdateLabel.report(f"{category_name} Category deleted :S")
        self.reorganize_cat_blocks()
#----------------------------------------------------------------------------------------------------#
    def reorganize_cat_blocks(self):
        # print("reordering cat blocks...")
        # Destroy all previously constructed cat blocks
        CardCatManager.destroy_all_blocks()

        # Calculate available columns
        canvas_width = self.categories_canvas.winfo_width()
        max_columns = max(1, canvas_width // CategoryBlock.min_width)
        num_of_total_categories = CardCatManager.categories_df.shape[0]
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

        # Recreate category blocks and pack them into column frames
        i = 0
        cat_block_row_insertion_order = CardCatManager.sorted_cat_order()
        for cat_block_row in cat_block_row_insertion_order:
            column_index = i % new_num_of_columns
            i += 1
            target_column_frame = self.column_frames[column_index]

            # Create the cat block in target column based on the row's info
            # Will fill itself in with cards automatically
            cat_block = CategoryBlock(
                target_column_frame,
                cat_block_row['keybind'],
                cat_block_row['name']
            )
            cat_block.pack(side=tk.TOP, fill=tk.X)
            CardCatManager.cat_blocks.append(cat_block)

        # Attach the cat blocks to the categories df, which will inherently share the same order
        CardCatManager.categories_df['cat_block'] = CardCatManager.cat_blocks

        # Update scrollregion
        self.categories_frame.update_idletasks()
        self.categories_canvas.update_idletasks()
        self.categories_canvas.configure(scrollregion=self.categories_canvas.bbox("inner_frame"))
#----------------------------------------------------------------------------------------------------#
    def on_window_resize(self, event):
        # Add this to avoid timing issues with canvas not growing correctly
        self.update_idletasks()

        # Leave some space for the scrollbar
        new_inner_width = self.categories_canvas.winfo_width() - self.scrollbar.winfo_width()
        self.categories_canvas.itemconfigure("inner_frame", width=new_inner_width)
        
        # Have category blocks fill in the new space
        self.reorganize_cat_blocks()

