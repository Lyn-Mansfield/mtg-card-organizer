import tkinter as tk
import re
from UpdateLabel import UpdateLabel
from CardEntryFrame import CardEntryFrame

root = tk.Tk()

# Body frame
body_frame = tk.Frame(root, highlightbackground='red', highlightthickness=4)
body_frame.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

# Header frame
header_frame = tk.Frame(body_frame, highlightbackground='purple', highlightthickness=4)
header_frame.pack(side=tk.TOP, fill=tk.X)

update_label = UpdateLabel(header_frame)
update_label.pack(side=tk.BOTTOM, expand=True, fill=tk.X)

card_entry_frame = CardEntryFrame(header_frame)
card_entry_frame.pack(side=tk.TOP, fill=tk.X)

bottom_frame = tk.Frame(body_frame, highlightbackground='blue', highlightthickness=4)
bottom_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

root.mainloop()