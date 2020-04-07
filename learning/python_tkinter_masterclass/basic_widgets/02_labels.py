# -*- coding: utf-8 -*-
import tkinter as tk

root = tk.Tk()
root.geometry("300x250")

label = tk.Label(root, text='A Sample Label')
label['text'] = 'An updated label'
label.config(text='Another way to update a label', fg='red')
label.config(bg='yellow')
label.config(font='Times 15')
label.config(text='Final update to label')
label.config(wraplength='100')
label.config(justify=tk.LEFT)  # Default is center, it seems
label.pack()

root.mainloop()
