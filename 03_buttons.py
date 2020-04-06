import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.geometry("350x300")

# THIS IS REALLY BAD AND SHOULD NOT HAPPEN
def callback():
    label.config(text='Button clicked',
                 fg='red',
                 bg='yellow')
    button['state'] = 'disabled'


label = tk.Label(root, text='Button Testing')
label.pack()

button = tk.Button(root, text='Tkinter Button', command=callback)
button.pack()

root.mainloop()