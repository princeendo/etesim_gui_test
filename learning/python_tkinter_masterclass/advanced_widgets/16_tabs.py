# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk


class TabsExample():
    def __init__(self, tk_root):
        iconfile = 'simple-icon.png'
        self.icon = tk.PhotoImage(file=iconfile)

        # Creating a Notebook seems to be the key to making tabs
        self.tabs = ttk.Notebook(tk_root,)

        # The fill can go horizontal (tk.X), vertical (tk.Y), or all (tk.BOTH)
        # I assume the "expand" keyword allows for it to fill the space
        self.tabs.pack(fill=tk.BOTH, expand=True)

        # Create a simple tab and add it. We can use this frame as a parent
        self.tab1 = ttk.Frame(self.tabs,)
        self.tabs.add(self.tab1, text='First Tab')

        # This tab will be the same as the first but will have an icon
        self.tab2 = ttk.Frame(self.tabs,)
        self.tabs.add(
                self.tab2,
                text='Second Tab',
                image=self.icon,        # The icon feature is awesome
                compound=tk.LEFT,)      # Places icon to the left of text


root = tk.Tk()
root.geometry("650x250+450+250")
app = TabsExample(root)
root.mainloop()
