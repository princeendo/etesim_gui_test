# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.geometry("300x150")


class CheckBoxes():
    def __init__(self, tk_root):
        # Header inside frame
        self.headerLabel = ttk.Label(text='Checkbox Display',
                                     font='Helvetica 9')
        self.headerLabel.grid(row=0, column=0, columnspan=2)

        # Getting username from user
        self.userLabel = ttk.Label(text='Username: ')
        self.userLabel.grid(row=1, column=0, sticky=tk.W)
        self.userEntry = tk.Entry(tk_root, width=30)
        self.userEntry.insert(0, 'e.g., "whitecr"')
        self.userEntry.grid(row=1, column=1)

        # Getting password from user
        self.passLabel = ttk.Label(text='Password: ')
        self.passLabel.grid(row=2, column=0, sticky=tk.W)
        self.passEntry = tk.Entry(tk_root, width=30)
        self.passEntry.insert(0, 'e.g., "1234"')
        self.passEntry.grid(row=2, column=1)

        self.submitButton = ttk.Button(tk_root, text='Submit')

        # Since sticky=tk.EW, it spans East and West
        # 'pady' gives it some vertical spacing
        self.submitButton.grid(row=3, column=1, sticky=tk.EW, pady=5,)
        self.submitButton.config(command=self.consolePrint)

        ####################################################################
        # The Checkbutton Part
        ####################################################################
        # You can alternatively use self.remember.set(False)
        # instead of value=False when setting the default value
        self.remember = tk.BooleanVar(value=False)
        self.rememberOnBox = tk.Checkbutton(tk_root,
                                            text='Remember Me',
                                            variable=self.remember,
                                            font='Arial 11')
        self.rememberOnBox.grid(row=4, column=0, sticky=tk.E, columnspan=2)

    def consolePrint(self):
        print(f'Username: {self.userEntry.get()}')
        print(f'Password: {self.passEntry.get()}')
        if self.remember.get():
            print('Remember me selected!')
        else:
            print('Not remembered')


app = CheckBoxes(root)
root.mainloop()
