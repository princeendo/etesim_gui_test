import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.geometry("500x450")

button1 = tk.Button(root, text='Tkinter Button')
button2 = ttk.Button(root, text='TTK Button')

button1.pack()
button2.pack()

root.mainloop()