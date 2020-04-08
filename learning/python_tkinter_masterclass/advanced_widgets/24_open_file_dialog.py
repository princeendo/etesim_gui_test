# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import filedialog


class OpenFileDialog():
    def __init__(self, tk_root):
        self.root = tk_root

        # A text window for displaying the contents of a file
        self.textEditor = tk.Text(self.root, width=25, height=15,)
        self.textEditor.pack()

        self.openButton = tk.Button(self.root, text='Open',
                                    command=self.openFileAppendContents)
        self.openButton.pack()

    # A callback function for opening a file and displaying its contents
    # Will append to whatever is currently in the text window
    def openFileAppendContents(self):
        kwargs = {'initialdir': 'C:\\',
                  'title': 'Select File',
                  'filetypes': (('Text Files', '.txt'),
                                ('All Files', '*.*'))}
        filename = filedialog.askopenfilename(**kwargs)
        with open(filename, 'r') as inp:
            self.textEditor.insert(tk.END, inp.read())

        # --- Equivalent form ---
        # filename = filedialog.askopenfilename(initialdir='C:\\',
        #                                       title='Select File',
        #                                       filetypes=(('Text Files',
        #                                                   '.txt'),
        #                                                  ('All Files',
        #                                                   '*.*')))


rt = tk.Tk()
rt.title('"Open File" Dialog Example')
rt.geometry("450x350+350+250")
app = OpenFileDialog(rt)
rt.mainloop()
