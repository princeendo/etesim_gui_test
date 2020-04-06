# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.geometry("300x300")

entry1 = ttk.Entry(root, width=30)
entry2 = tk.Entry(root, width=30)
entry3 = tk.Entry(root, width=30)
entry1.insert(0, 'TTK Input Box')
entry2.insert(0, 'TK Input Box')
entry3.insert(0, 'Password')
entry3.config(show='*')

entry1.pack()
entry2.pack()
entry3.pack()

# THIS IS REALLY BAD AND SHOULD NOT HAPPEN
# This only works with defined globals. Kind of pisses me off.
def callback():
    val1 = entry1.get()
    val3 = entry3.get()
    print(f'The value in the first box is "{val1}"')
    print(f'The password is {val3}')
    
    # TTK can use .state()
    # Options are disabled, !disabled, readonly
    entry1.state(['readonly'])
    
    # TK must use .config(state=) for the same behavior
    # Options are distabled, normal, or readonly for tk
    entry2.config(state='disabled')
    entry3.config(state='normal')


label = tk.Label(root, text='Button Testing')
label.pack()

button = tk.Button(root, text='Activation Button', command=callback)
button.pack()

root.mainloop()
