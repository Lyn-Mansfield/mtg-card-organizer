import tkinter as tk
from tkinter import ttk
from CategoryBlock import CategoryBlock
from UpdateLabel import UpdateLabel

class CategoryBlockFrame(tk.Frame):
    def __init__(self, root, delete_cat_command=None, **kwargs):
        # Everything lives in self
        super().__init__(root, **kwargs)
        self.bind('<Configure>', self.on_window_resize)

        # Category/Keybind storage
        self.cat_blocks = {}
        self.key_bindings = {}
        self.all_items = set([])

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
    def _on_keystroke(self, curr_cat_block, event):
        """Handle key presses for moving cards from category to category"""
        print('generic keystroke detected...')
        print(event.keysym)

        match event.keysym:
            case "BackSpace" | "Delete":
                curr_cat_block.delete_selected_entry()
            case "equal":
                curr_cat_block.add()
            case "plus":
                curr_cat_block.add_5()
            case "minus":
                curr_cat_block.subtract()
            case "underscore":
                curr_cat_block.subtract_5()
            case _:
                self._transfer_card(curr_cat_block, event.char)
#----------------------------------------------------------------------------------------------------#
    def _transfer_card(self, curr_cat_block, keybind):
        if keybind not in self.key_bindings.keys():
            return
        if curr_cat_block.size() == 0:
            return

        selected_index = curr_cat_block.selected_index()
        selected_card = curr_cat_block.get(selected_index)
        target_category_name = self.key_bindings[keybind]
        target_cat_block = self.cat_blocks[target_category_name]

        # Remove from current block, transfer to new block
        curr_cat_block.delete(selected_index)
        target_cat_block.insert(selected_card)
        # Go to the card after it's been moved
        target_cat_block.goto(tk.END)

        UpdateLabel.report(f"{selected_card} moved from {curr_cat_block.name} to {target_cat_block.name} c:")
#----------------------------------------------------------------------------------------------------#
    def add_category(self, keybind, category_name):
        # Initialize root to the categories frame
        new_cat_block = CategoryBlock(
            self.categories_frame, 
            self,
            keybind,
            category_name, 
            self._on_keystroke, 
            self.delete_cat_command
        )

        # Update dictionaries
        self.cat_blocks[category_name] = new_cat_block
        self.key_bindings[keybind] = category_name

        UpdateLabel.report(f"{category_name} Category added c:")
        # Reorganize the blocks
        self.reorganize_cat_blocks()
#----------------------------------------------------------------------------------------------------#
    def delete_category(self, category_name):
        deleted_cat_block = self.cat_blocks[category_name]
        deleted_keybind = deleted_cat_block.keybind

        del self.key_bindings[deleted_keybind]
        del self.cat_blocks[category_name]
        self.all_items -= deleted_cat_block.all_items
        deleted_cat_block.destroy()

        UpdateLabel.report(f"{category_name} Category deleted :S")
        self.reorganize_cat_blocks()
#----------------------------------------------------------------------------------------------------#
    def reorganize_cat_blocks(self):
        # Calculate available columns
        canvas_width = self.categories_canvas.winfo_width()
        max_columns = max(1, canvas_width // CategoryBlock.min_width)
        num_of_total_categories = len(self.cat_blocks)
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
        for cat_name, cat_block in self.cat_blocks.items():
            column_index = i % new_num_of_columns
            i += 1
            target_column_frame = self.column_frames[column_index]

            # Clone the block frame into its new column frame
            cat_block.pack_forget()
            cat_block_clone = cat_block.copy(new_root=target_column_frame)
            cat_block_clone.pack(side=tk.TOP, expand=True, fill=tk.X)

            # Update references to clones
            self.cat_blocks[cat_name] = cat_block_clone
            cat_block.destroy()

        # Update scrollregion
        self.categories_frame.update_idletasks()
        self.categories_canvas.update_idletasks()
        self.categories_canvas.configure(scrollregion=self.categories_canvas.bbox("inner_frame"))
#----------------------------------------------------------------------------------------------------#
    def add_new_item(self, new_item, target_category):
        target_cat_block_frame = self.cat_blocks[target_category]
        if new_item in self.all_items:
            UpdateLabel.report(f'{new_item} is already added :S')
            return
            
        target_cat_block_frame.insert(new_item)
#----------------------------------------------------------------------------------------------------#
    def on_window_resize(self, event):
        # Add this to avoid timing issues with canvas not growing correctly
        self.update_idletasks()

        # Leave some space for the scrollbar
        new_inner_width = self.categories_canvas.winfo_width() - self.scrollbar.winfo_width()
        self.categories_canvas.itemconfigure("inner_frame", width=new_inner_width)
        
        # Have category blocks fill in the new space
        self.reorganize_cat_blocks()

