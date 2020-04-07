# -*- coding: utf-8 -*-
import tkinter as tk


# For AxB+C+D, the values follow:
# A: width
# B: height
# C: Start X location (from left)
# D: Start Y location (from top)
root = tk.Tk()
root.geometry("450x450+650+350")


class PlaceGeometryManager():
    def __init__(self, tk_root):
        self.title = tk.Label(tk_root,
                              text='Place Geometry Manager',
                              font=(("Verdana"), 15),)
        self.title.place(x=100,  # pixels from left
                         y=20,)  # pixels from top

        self.name_txt = tk.Label(tk_root, text='Name: ')
        self.name_txt.place(x=20, y=80,)

        self.name_input = tk.Entry(tk_root, width=30,)
        self.name_input.place(x=100, y=80,)

        self.pass_txt = tk.Label(tk_root, text='Pass: ')
        self.pass_txt.place(x=20, y=110,)

        self.pass_input = tk.Entry(tk_root, width=30,)
        self.pass_input.place(x=100, y=110,)

        self.button1 = tk.Button(root, text='Save',)
        self.button1.place(x=250, y=135,)

        # The relx/rely values are related to the window size
        # So if you resize the window, the locations scale
        self.button2 = tk.Button(root,
                                 text='Click Me',
                                 bg='red').place(relx=0.5,   # Percentages from
                                                 rely=0.9,)  # top(y)/left(x)


app = PlaceGeometryManager(root)
root.mainloop()
