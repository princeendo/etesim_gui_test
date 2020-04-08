# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk


class ListBoxWidget():
    def __init__(self, tk_root):

        # Listbox is a list of items that you can select
        # Not rocket science
        self.listBox = tk.Listbox(tk_root,
                                  width=40,
                                  height=15,
                                  selectmode=tk.MULTIPLE,)  # Single also works
        self.listBox.insert(0, 'First Item')
        self.listBox.insert(1, 'Second Item')
        self.listBox.insert(2, 'Third Item')
        self.listBox.insert(3, 'Fourth Item')
        self.listBox.pack(pady=25)

        # Adding a couple of buttons (notice we can mix pack() and place())
        # to demonstrate various functionality
        self.button1 = tk.Button(
                            tk_root,
                            text='Print',
                            command=self.consolePrint,).place(x=300, y=300,)
        self.button2 = tk.Button(
                            tk_root,
                            text='Delete',
                            command=self.itemDelete,).place(x=350, y=300,)

    def consolePrint(self,):
        for item in self.listBox.curselection():
            print(self.listBox.get(item))

    # This will not delete correctly if you go in forward order
    # If you delete a value at index 0, the value at index 2 will be
    # the value that was previously at index 3. So you need to iterate
    # in reverse to avoid this issue.
    def itemDelete(self,):
        for item in reversed(list(self.listBox.curselection())):
            self.listBox.delete(item)


root = tk.Tk()
root.geometry("650x450+450+150")
app = ListBoxWidget(root)
root.mainloop()
