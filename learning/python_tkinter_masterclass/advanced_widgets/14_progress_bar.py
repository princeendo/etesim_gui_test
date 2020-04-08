# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk


class ProgressBar():
    def __init__(self, tk_root):
        self.progbar = ttk.Progressbar(tk_root,
                                       orient=tk.HORIZONTAL,  # vert/hor bar
                                       length=200,)
        self.progbar.pack(pady=20)
        self.progbar.config(mode='determinate',
                            maximum=100.0,
                            value=50.0,)
        # The value paramter is usually set at regular intervals
        # (updated by a function3)

        # In "indeterminate" mode you can use these functions to
        # force behavior
        # self.progbar.start()
        # self.progbar.stop()
        self.value = tk.DoubleVar()
        self.progbar.config(variable=self.value)
        self.scale = ttk.Scale(root,
                               orient=tk.HORIZONTAL,
                               length=200,
                               var=self.value,  # Stores output in self.value
                               from_=0.0,       # Minimum value
                               to=50.0,)        # Maximum value
        self.scale.pack()

root = tk.Tk()
root.geometry("450x450+650+350")
app = ProgressBar(root)
root.mainloop()
