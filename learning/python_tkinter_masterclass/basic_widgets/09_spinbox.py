# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.geometry("300x200")


class SpinBox():
    def __init__(self, tk_root):
        # Header inside frame
        self.headerLabel = ttk.Label(text='Checkbox Display',
                                     font='Helvetica 9')
        self.headerLabel.grid(row=0, column=0, columnspan=3)

        # Getting username from user
        self.username = tk.StringVar()
        self.usernameLabel = ttk.Label(text='Username: ')
        self.usernameLabel.grid(row=1, column=0, sticky=tk.W)
        self.usernameEntry = tk.Entry(tk_root, width=30,
                                      textvariable=self.username,)
        self.usernameEntry.insert(0, 'e.g., "whitecr"')
        self.usernameEntry.grid(row=1, column=1, columnspan=2)

        # Getting password from user
        self.password = tk.StringVar()
        self.passwordLabel = ttk.Label(text='Password: ')
        self.passwordLabel.grid(row=2, column=0, sticky=tk.W)
        self.passwordEntry = tk.Entry(tk_root, width=30,
                                      textvariable=self.password,)
        self.passwordEntry.insert(0, 'e.g., "1234"')
        self.passwordEntry.grid(row=2, column=1, columnspan=2)

        self.submitButton = ttk.Button(tk_root, text='Submit')

        # Since sticky=tk.EW, it spans East and West
        # 'pady' gives it some vertical spacing
        self.submitButton.grid(row=3, column=1, sticky=tk.EW, pady=5, padx=8)
        self.submitButton.config(command=self.consolePrint)

        # You can alternatively use self.remember.set(False)
        # instead of value=False when setting the default value
        self.remember = tk.BooleanVar(value=False)
        self.rememberOnBox = tk.Checkbutton(tk_root,
                                            text='Remember',
                                            variable=self.remember,
                                            font='Arial 9')
        self.rememberOnBox.grid(row=3, column=2, sticky=tk.E, columnspan=2)

        # Asking for gender from user given binary options (Not woke!)
        # The default (i.e., unselected) value is an empty string
        self.gender = tk.StringVar()
        self.genderLabel = ttk.Label(text='Gender: ')
        self.genderLabel.grid(row=4, column=0)
        self.maleRadio = ttk.Radiobutton(root,
                                         text='male',       # Button text
                                         value='male',      # Stored value
                                         var=self.gender,)
        self.maleRadio.grid(row=4, column=1)
        self.femaleRadio = ttk.Radiobutton(root,
                                           text='female',   # Button text
                                           value='female',  # Stored value
                                           var=self.gender,)
        self.femaleRadio.grid(row=4, column=2)

        # Setting up a dropdown menu
        # You can specify the options inline but it seems cleaner
        # to set them up as options to edit here
        month_options = ('January', 'February', 'March', 'April')
        self.monthLabel = ttk.Label(text='Month: ')
        self.monthLabel.grid(row=5, column=0)
        self.month = tk.StringVar()
        self.monthComboBox = ttk.Combobox(tk_root,
                                          textvariable=self.month,
                                          values=month_options,
                                          state='readonly',
                                          width=30,)
        self.monthComboBox.grid(row=5, column=1, columnspan=2)

        ####################################################################
        # The Spinbox Part
        ####################################################################
        # Setting up a 'spinbox' where you can only select a range of values
        self.year = tk.StringVar()
        self.yearLabel = ttk.Label(text='Year:  ')
        self.yearLabel.grid(row=6, column=0)

        # This can be done with tk or ttk
        # If using tk, the default value is from_ or use the "value" keyword
        # If using ttk, you have to set the default value with .set()
        self.yearSpinBox = ttk.Spinbox(tk_root,
                                       from_=1990,
                                       to=2018,
                                       value=1995,
                                       textvariable=self.year,
                                       width=30,
                                       state='readonly',)  # to limit input
        self.yearSpinBox.insert(0, '1995')
        self.yearSpinBox.grid(row=6, column=1, columnspan=2)
        self.yearSpinBox.set('1994')

    def consolePrint(self):
        print(f'Username: {self.username.get()}')
        print(f'Password: {self.password.get()}')
        if self.remember.get():
            print('Remember me selected!')
        else:
            print('Not remembered')
        if self.gender.get():
            print(f'Gender:   {self.gender.get()}')
        else:
            print('Gender not selected')
        if self.month.get():
            print(f'Month:    {self.month.get()}')
        else:
            print('Month not selected')


app = SpinBox(root)
root.mainloop()
