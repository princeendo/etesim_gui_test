# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox as mb


class MenuBar():
    def __init__(self, tk_root):
        self.root = tk_root

        self.menuBar = tk.Menu(self.root)
        self.root.config(menu=self.menuBar)

        # Creating the menus items which will drop down
        self.fileDropDown = tk.Menu(self.menuBar,
                                    tearoff=0)  # Hides "perforated" line
        self.editDropDown = tk.Menu(self.menuBar)
        self.aboutDropDown = tk.Menu(self.menuBar)

        self.menuBar.add_cascade(label='File', menu=self.fileDropDown,)
        self.menuBar.add_cascade(label='Edit', menu=self.editDropDown,)
        self.menuBar.add_cascade(label='About', menu=self.aboutDropDown,)

        self.fileDropDown.add_command(label='New')
        self.fileDropDown.add_separator()            # Adds segmentation bar
        self.fileDropDown.add_command(label='Open')
        self.fileDropDown.add_command(label='Save')
        self.quitIcon = tk.PhotoImage(file='Gtk-quit.png')
        self.fileDropDown.add_command(label='Exit', image=self.quitIcon,
                                      compound=tk.LEFT, command=self.Quit)

    def Quit(self):
        mbox = mb.askquestion('Exit', 'Are you sure you want to quit?',
                              icon='warning')
        if mbox == 'yes':
            self.root.destroy()


rt = tk.Tk()
rt.geometry("650x450+450+150")
app = MenuBar(rt)
rt.mainloop()
