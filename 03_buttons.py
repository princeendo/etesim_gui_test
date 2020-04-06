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

'''
label['text'] = 'An updated label'
label.config(text='Another way to update a label', fg='red')
label.config(bg='yellow')
label.config(font='Times 15')
label.config(text='Final update to label')
label.config(wraplength='100')
label.config(justify=tk.LEFT) # Default is center, it seems
label.pack()
'''

root.mainloop()