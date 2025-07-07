import tkinter as tk
import re

root = tk.Tk()

Lb1 = tk.Listbox(root)
Lb1.pack(side=tk.TOP)
Lb1.insert(1, "Python")
Lb1.insert(2, "Perl")
Lb1.insert(3, "C")
Lb1.insert(4, "PHP")
Lb1.insert(5, "JSP")
Lb1.insert(6, "Ruby")

all_items = Lb1.get(0, tk.END)  # Get all items as a list
item_exists = "Perl" in all_items
print(item_exists)

Lb1.pack()
root.mainloop()