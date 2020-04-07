# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox as mb
from tkinter import ttk

root = tk.Tk()
root.geometry("350x250")


# A class for demonstrating how to make a message box
class MessageBox():
    def __init__(self, tk_root):

        # Creating a dialog button
        self.promptButton = ttk.Button(tk_root,
                                       text='Delete',
                                       command=self.promptQuestion)
        self.promptButton.grid(row=0, column=0, pady=25, padx=50)

        # Creating a button that provides information
        self.infoButton = ttk.Button(tk_root,
                                     text='Info',
                                     command=self.infoMessage)
        self.infoButton.grid(row=0, column=1)

    def promptQuestion(self):

        mbox = mb.askquestion('Delete',         # First argument is box title
                              'Are you sure?',  # Second is box text
                              icon='warning',)
        out = 'Deleted' if mbox == 'yes' else 'Kept'
        print(out)

    def infoMessage(self):
        # Note: showinfo() returns "ok" when the box is clicked
        mb.showinfo('Success',     # First argument is box title
                    'Well Done',)  # Second is box text


app = MessageBox(root)
root.mainloop()
