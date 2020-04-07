# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.geometry("300x300")


class EntryWidget():
    def __init__(self, tk_root):
        # Generating one ttk instance and two tk instances
        self.entry1 = ttk.Entry(root, width=30)
        self.entry2 = tk.Entry(root, width=30)
        self.entry3 = tk.Entry(root, width=30)

        # Inserting text at, I guess, the 0th character entry
        # I don't actually think that's true, though.
        # Modifying to any other number seems to do nothing
        self.entry1.insert(0, 'TTK Input Box')
        self.entry2.insert(0, 'TK Input Box')

        # Setting a password field to show up as asterisks instead
        self.entry3.insert(0, 'Password')
        self.entry3.config(show='*')

        # Making sure these show up
        self.entry1.pack()
        self.entry2.pack()
        self.entry3.pack()

        # Labels and buttons - covered previously
        self.label = tk.Label(tk_root, text='Button Testing')
        self.label.pack()
        self.button = tk.Button(tk_root,
                                text='Activation Button',
                                command=self.callback)
        self.button.pack()

    def callback(self):
        print(f'The value in the first box is "{self.entry1.get()}"')
        print(f'The password is {self.entry3.get()}')

        # TTK can use .state()
        # Options are disabled, !disabled, readonly
        self.entry1.state(['readonly'])

        # TK must use .config(state=) for the same behavior
        # Options are distabled, normal, or readonly for tk
        self.entry2.config(state='disabled')


app = EntryWidget(root)
root.mainloop()
