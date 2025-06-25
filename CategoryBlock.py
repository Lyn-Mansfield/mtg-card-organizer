import tkinter as tk

class CategoryBlock:
    # Category block configuration
    min_width = 250
    min_height = 8
    block_padding = 5

    def __init__(self, root, label_name, transfer_command, data=None):
        if not isinstance(label_name, str): raise TypeError("label_name must be a str")
        if data is not None and not hasattr(data, '__iter__'): raise TypeError("data must be iterable")

        self.root = root
        self.whole_frame = tk.Frame(
            self.root,
            height=300,
            width=self.min_width,
            highlightbackground='blue',
            highlightthickness=1
        )

        # Category label
        self.label = tk.Label(
            self.whole_frame, 
            text=label_name
        )
        self.label.pack(side=tk.TOP)

        # Cards listbox
        self.listbox = tk.Listbox(
            self.whole_frame,
            height=self.min_height
        )
        if data is not None:
            self.listbox.insert(tk.END, *data)
        self.listbox.pack(side=tk.TOP, expand=True, fill=tk.X)

        # Bind transfer command
        self.transfer_command = transfer_command
        self.listbox.bind('<Key>', lambda event: self.transfer_command(self, event))

    def copy(self, new_root=None):
        if new_root is None:
            new_root = self.root

        label_name = self.label.cget("text")
        listbox_data = self.listbox.get(0, tk.END)
        transfer_command = self.transfer_command
        cat_block_clone = CategoryBlock(new_root, label_name, transfer_command, data=listbox_data)
        return cat_block_clone

    def size(self):
        return self.listbox.size()

    def curselection(self):
        return self.listbox.curselection()

    def get(self, index):
        return self.listbox.get(index)

    def add(self, new_item):
        self.listbox.insert(tk.END, new_item)

        # Auto-grow the listbox height
        item_count = self.listbox.size()
        new_size = max(self.min_height, item_count)
        self.listbox.config(height=new_size)

    def delete(self, index):
        self.listbox.delete(index)

    def delete_selected_entry(self, event=None):
        print('trying to delete!')
        selected_index = self.listbox.curselection()
        self.delete(selected_index)

    def pack(self, side=None, padx=None, pady=None, expand=False, fill=None):
        if padx is None:
            padx = self.block_padding
        if pady is None:
            pady = self.block_padding
        self.whole_frame.pack(side=side, padx=padx, pady=pady, expand=expand, fill=fill)

    def pack_forget(self):
        self.whole_frame.pack_forget()

    def destroy(self):
        self.whole_frame.destroy()