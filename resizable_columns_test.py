import tkinter as tk
from tkinter import ttk

class MultiColumnListboxApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dynamic Multi-Column Listboxes")
        
        # Configuration
        self.min_listbox_width = 200
        self.min_listbox_height = 3
        self.padding = 5
        
        # Data storage for each listbox
        self.listboxes = []
        self.listbox_data = []
        
        # Input frame
        self.input_frame = ttk.Frame(root)
        self.input_frame.pack(padx=10, pady=5, fill=tk.X)
        
        # Entry and buttons
        self.entry = ttk.Entry(self.input_frame)
        self.entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        
        self.target_var = tk.IntVar(value=0)
        self.target_selector = ttk.OptionMenu(
            self.input_frame, self.target_var, *[], 
            command=lambda _: self.entry.focus()
        )
        self.target_selector.pack(side=tk.LEFT, padx=(0, 5))
        
        self.add_button = ttk.Button(
            self.input_frame, text="Add", command=self.create_new_category
        )
        self.add_button.pack(side=tk.LEFT)
        
        # Container frame for listboxes
        self.categories_frame = ttk.Frame(root)
        self.categories_frame.pack(padx=10, pady=(0, 10), expand=True, fill=tk.BOTH)
        
        # Initial setup
        self.create_new_category()
        self.entry.bind('<Return>', lambda event: self.add_item())
        
        # Bind window resize event
        self.root.bind('<Configure>', self.on_window_resize)
    
    def create_new_category(self):
        """Create a new listbox and add it to our collection"""
        next_index_str = str(len(self.listboxes))

        new_cat_frame = tk.Frame(
            self.categories_frame,
            height=300,
            width=self.min_listbox_width,
            highlightbackground='blue',
            highlightthickness=1
        )
        new_cat_frame.label = tk.Label(new_cat_frame, text=next_index_str)
        new_cat_frame.label.pack(side=tk.TOP)
        new_cat_frame.listbox = tk.Listbox(
            new_cat_frame,
            height=self.min_listbox_height,
            width=self.min_listbox_width # Initial width
        )
        new_cat_frame.listbox.pack(side=tk.TOP)
        self.listboxes.append(new_cat_frame)
        self.listbox_data.append([])
        
        # Update target selector
        self.target_selector['menu'].add_command(
            label=next_index_str,
            command=tk._setit(self.target_var, next_index_str)
        )
        
        self.reorganize_listboxes()
    
    def add_item(self):
        """Add an item to the selected listbox"""
        target_idx = self.target_var.get()
        if target_idx > len(self.listboxes):
            return
            
        new_item = self.entry.get()
        if new_item:
            target_listbox = self.listboxes[target_idx].listbox
            target_listbox.insert(tk.END, new_item)
            self.listbox_data[target_idx].append(new_item)
            self.entry.delete(0, tk.END)
            
            # Auto-grow the listbox height
            item_count = target_listbox.size()
            target_listbox.config(height=item_count)
    
    def reorganize_listboxes(self):
        """Calculate optimal columns and reposition listboxes"""
        # Clear current packing
        for listbox in self.listboxes:
            listbox.pack_forget()
        
        # Calculate available columns
        frame_width = self.categories_frame.winfo_width()
        if frame_width < self.min_listbox_width * 1.5:  # Prevent single column from being too narrow
            frame_width = self.min_listbox_width * 1.5
        
        max_columns = max(1, int(frame_width / self.min_listbox_width))
        columns = min(max_columns, len(self.listboxes))
        
        # Repack listboxes in grid layout
        for i, listbox in enumerate(self.listboxes):
            row = i // columns
            col = i % columns
            listbox.grid(
                row=row, 
                column=col, 
                padx=self.padding, 
                pady=self.padding, 
                sticky="nsew"
            )
        
        # Configure grid weights
        for c in range(columns):
            self.categories_frame.columnconfigure(c, weight=1)
        for r in range((len(self.listboxes) + columns - 1) // columns):
            self.categories_frame.rowconfigure(r, weight=0)  # Don't expand rows vertically
    
    def on_window_resize(self, event):
        """Handle window resize events"""
        if event.widget == self.root:
            self.reorganize_listboxes()

if __name__ == "__main__":
    root = tk.Tk()
    app = MultiColumnListboxApp(root)
    root.mainloop()