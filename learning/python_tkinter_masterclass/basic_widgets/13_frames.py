# -*- coding: utf-8 -*-
import tkinter as tk

root = tk.Tk()
root.title('Frames Example')
root.geometry("650x650+450+200")


# Reference: http://effbot.org/tkinterbook/frame.htm
class FrameTest():
    def __init__(self, tk_root):
        self.topFrame = tk.Frame(tk_root,
                                 height=300, width=300,  # dimensions of frame
                                 background='red',   # Can use "bg" instead
                                 borderwidth='7',    # Can use "bd" instead
                                 relief=tk.SUNKEN,)  # Requires bd setting

        # This works with the "bg" setting
        self.topFrame.pack(fill=tk.X)

        self.button1 = tk.Button(self.topFrame,     # Has parent of frame
                                 text='Button1',)
        self.button1.pack(side=tk.LEFT,             # Aligns left
                          padx=20,                  # 20px buffer left/right
                          pady=5)                   # 5px buffer top/bottom

        self.button2 = tk.Button(self.topFrame,     # Has parent of frame
                                 text='Button2',)
        # Has left alignment, but since button1 has already been packed,
        # It will be to the right of button1 and the left edge will be
        # the padding on button1. Adding a padx here will pad button2,
        # as well, so you end up with a double padding
        self.button2.pack(side=tk.LEFT,
                          padx=10)

        # Reference: http://effbot.org/tkinterbook/labelframe.htm
        # Creates a nice frame wrapper for an object
        self.searchBar = tk.LabelFrame(tk_root,
                                       text='Search Box',
                                       background='#fcd45d',)  # hex value
        self.searchBar.pack(side=tk.TOP, padx=10,)

        # Label is attached to searchBar, not root
        self.searchLabel = tk.Label(self.searchBar, text='Search')
        self.searchLabel.pack(side=tk.LEFT, padx=10,)

        # Entry is attached to searchBar, not root or other frame
        self.searchEntry = tk.Entry(self.searchBar)
        self.searchEntry.pack(side=tk.LEFT, padx=10,)

        # Button is attached to searchBar, not root or other frame
        self.searchButton = tk.Button(self.searchBar, text='Search')
        self.searchButton.pack(side=tk.LEFT, padx=10)


app = FrameTest(root)
root.mainloop()
