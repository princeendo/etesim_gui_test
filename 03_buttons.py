# -*- coding: utf-8 -*-
import tkinter as tk

root = tk.Tk()
root.geometry("350x300")


# Updated his stupid way of doing things with globals
# Favoring an OOP approach
class ButtonMaker():
    def __init__(self, tk_root):
        self.lbltext = 'Button Testing'
        self.label = tk.Label(tk_root, text=self.lbltext)
        self.label.pack()

        # Consult https://effbot.org/tkinterbook/button.htm
        buttontext = 'Tkinter Button'
        self.button = tk.Button(tk_root,
                                text=buttontext,
                                command=self.callback)
        self.button.pack()

    def callback(self):
        self.label.config(text='Button clicked',
                          fg='red',
                          bg='yellow')
        self.button['state'] = 'disabled'


app = ButtonMaker(root)
root.mainloop()
