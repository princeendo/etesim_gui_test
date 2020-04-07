# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.geometry("500x450")


# Placing items with grid specification is very powerful
# It seems to auto-adjust width so that column 2
# would start at the end of column 1, no matter the width
class GridLayout():
    def __init__(self, tk_root):
        # Username entry
        self.entry1 = ttk.Entry(root, width=30)
        self.entry1.insert(0, 'Please enter your name')
        self.entry1.grid(row=1, column=1)

        # Password Entry
        self.entry2 = ttk.Entry(root, width=30)
        self.entry2.insert(0, 'Please enter your password')
        self.entry2.grid(row=2, column=1)

        # Submit button
        self.button = ttk.Button(root, text='Submit')
        self.button.grid(row=3, column=1, sticky=tk.EW, pady=5)

        # Setting an obscenely large title
        self.lbltitle = ttk.Label(text='Grid Layout Test',
                                  font=(('Arial'), 22))

        # columnspan allows it to cover both sections
        self.lbltitle.grid(row=0, column=0, columnspan=2)

        # Setting up the labeling of the fields for username/password
        self.userlabel = ttk.Label(text='Your Name :)')
        self.userlabel.grid(row=1, column=0, sticky=tk.W)
        self.passlabel = ttk.Label(text='Your Password :)')
        self.passlabel.grid(row=2, column=0, sticky=tk.W)


app = GridLayout(root)
root.mainloop()
