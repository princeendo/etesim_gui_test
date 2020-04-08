# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk


class PanedWindow():
    def __init__(self, tk_root):
        self.pw = ttk.Panedwindow(tk_root,
                                  orient=tk.HORIZONTAL)
        self.pw.pack(fill=tk.BOTH,
                     expand=True)
        self.frame1 = ttk.Frame(self.pw, width=100, height=500,
                                relief=tk.SUNKEN,)
        self.frame2 = ttk.Frame(self.pw, width=300, height=500,
                                relief=tk.SUNKEN,)
        self.frame3 = ttk.Frame(self.pw, width=75, height=500,
                                relief=tk.SUNKEN,)

        # The "weight" parameter gives a relative sizing
        # This is based on orientation, which here is horizontal
        self.pw.add(self.frame1, weight=1)
        self.pw.add(self.frame2, weight=3)

        # This inserts into the 1st index (frame1 is at index 0)
        # You cannot insert at index 2. You would need to use .add()
        self.pw.insert(1, self.frame3,)

        # Adds a block of text to the first frame
        # Notice how self.frame1 is the parent, not tk_root
        self.lbl = tk.Label(self.frame1, text='Hello',).grid(row=0,
                                                             column=0,
                                                             padx=10,
                                                             pady=25)
        # Adds a button to the second frame
        # Notice how self.frame3 is actually the middle frame
        # Notice how self.frame2 is the parent, not tk_root
        self.button = ttk.Button(self.frame2, text='Click',).grid(row=1,
                                                                  column=0,
                                                                  padx=20,
                                                                  pady=55)


root = tk.Tk()
root.geometry("650x250+450+250")
app = PanedWindow(root)
root.mainloop()
