# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk


class UseImages():
    def __init__(self, tk_root):
        # Realy just a title
        self.bigLabel = tk.Label(tk_root,
                                 text='Using Images',
                                 font=(("Times"), 18))
        self.bigLabel.pack()

        # Set up icon to be displayed in the GUI
        self.iconfile = 'simple-icon.png'
        self.logo = tk.PhotoImage(file=self.iconfile)

        # This label has no text but instead has an image
        self.imageLabel = tk.Label(tk_root, image=self.logo)
        self.imageLabel.pack()


root = tk.Tk()
root.title('Using Images')
root.geometry("350x350")
app = UseImages(root)
root.mainloop()
