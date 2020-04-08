# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk


class Scrollbar():
    def __init__(self, tk_root):
        self.root = tk_root

        # Creating a simple text box that wraps on a word
        self.textBox = tk.Text(self.root, width=60, height=20, wrap='word')
        self.textBox.grid(row=0, column=0)

        # Reference: http://effbot.org/zone/tkinter-scrollbar-patterns.htm
        # I believe the .yview() function tells you where to place the
        # viewing of the text box. It sort of updates where the "top" is
        self.scrollBar = ttk.Scrollbar(self.root,
                                       orient=tk.VERTICAL,
                                       command=self.textBox.yview)
        self.scrollBar.grid(row=0, column=1, sticky=tk.NS)

        # This allows for that grabbable nub in the scrollbar
        # so you don't have to use the arrows
        # Trust me, you want this
        self.textBox.config(yscrollcommand=self.scrollBar.set)


rt = tk.Tk()
rt.title('Scrollbar Sample')
rt.geometry('500x450')
app = Scrollbar(rt)
rt.mainloop()
