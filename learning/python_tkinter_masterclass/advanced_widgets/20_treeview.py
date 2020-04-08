# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk


class TreeView():
    def __init__(self, tk_root):
        self.root = tk_root

        # Setting up icons for examples
        # icon0, icon1, and icon2 are just checkmarks
        # icon3 is a power off button
        self.icons = [tk.PhotoImage(file=f'icon{i}.png')
                      for i in range(4)]

        self.tv = ttk.Treeview(self.root)
        self.tv.pack()

        # Adding items to the list
        # Using enumerate and some titles to show how to do this procedurally
        # Equivalent to
        # self.tv.insert('', '0', 'item1', text='First Item',
        #                image=self.icons[0])
        # self.tv.insert('', '1', 'item1', text='Second Item',
        #                image=self.icons[1])
        # self.tv.insert('', '2', 'item1', text='Third Item',
        #                image=self.icons[2])
        # self.tv.insert('', '3', 'item1', text='Fourth Item',
        #                image=self.icons[3])
        for idx, name in enumerate(['First', 'Second', 'Third', 'Fourth', ]):
            parent = ''
            iid = f'item{idx}'
            item_name = f'{name} Item'
            self.tv.insert(parent, str(idx), iid, text=item_name,
                           image=self.icons[idx])

        # Moving item (first argument) under parent (second argument)
        # at the given index (can use 'end' or 'begin' here, as well)
        child = 'item2'
        parent = 'item0'
        loc = 'end'
        self.tv.move(child, parent, loc)

        # Adding the ability to capture double-clicks
        self.tv.bind('<Double-1>', self.consolePrint)

    def consolePrint(self, event):
        # My guess is that "event.x" is the x location in pixels (from left)
        # and that "event.y" is the y location in pixels (from top)
        print(f'Event X: {event.x}')
        print(f'Event Y: {event.y}')
        item = self.tv.identify('item', event.x, event.y)
        val = self.tv.item(item, "text")
        print(f'Clicked on {val}')


rt = tk.Tk()
rt.title('TreeView Sample')
rt.geometry("650x450+450+150")
app = TreeView(rt)
rt.mainloop()
