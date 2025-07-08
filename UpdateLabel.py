import tkinter as tk
from tkinter import ttk

class UpdateLabel(tk.Label):
    _message = ''  # Class-level message storage
    _instances = []  # Track all label instances

    def __init__(self, root, **kwargs):
        super().__init__(root, text=self._message, **kwargs)
        self._instances.append(self)  # Register new instance

    @classmethod
    def report(cls, update_msg):
        cls._message = update_msg
        for label in cls._instances:  # Update all existing labels
            label.config(text=update_msg)
            label.update_idletasks()  # Force immediate GUI update

    @classmethod
    def clear(cls):
        cls.report("")  # Clear all labels

    def destroy(self):
        self._instances.remove(self)  # Clean up on destruction
        super().destroy()