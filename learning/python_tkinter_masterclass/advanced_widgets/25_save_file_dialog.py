# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import filedialog


class SaveFileDialog():
    def __init__(self, tk_root):
        self.root = tk_root

        # A text window for displaying the contents of a file
        self.textEditor = tk.Text(self.root, width=25, height=15,)
        self.textEditor.pack()

        self.openButton = tk.Button(self.root, text='Open',
                                    command=self.openFileAppendContents)
        self.openButton.pack(side=tk.LEFT, padx=(170, 20))

        self.saveButton = tk.Button(self.root, text='Save',
                                    command=self.saveTextToFile)
        self.saveButton.pack(side=tk.LEFT,)

    # A callback function for saving the contents of the text box.
    # I had to write some extra kwargs because the instructor SUCKKKKS
    def saveTextToFile(self):
        kwargs = {'initialdir': 'C:\\',
                  'title': 'Output Filename',
                  'filetypes': (('Text Files', '.txt'),
                                ('All Files', '*.*')),
                  'defaultextension': '.txt',
                  'mode': 'w',
                  }

        myfile = filedialog.asksaveasfile(**kwargs)
        if myfile is None:
            return
        content = self.textEditor.get(1.0, 'end-1c')  # drop last character
        myfile.write(content)

    # A callback function for opening a file and displaying its contents
    # Will append to whatever is currently in the text window
    def openFileAppendContents(self):
        # --- Equivalent form ---
        # filename = filedialog.askopenfilename(initialdir='C:\\',
        #                                       title='Select File',
        #                                       filetypes=(('Text Files',
        #                                                   '.txt'),
        #                                                  ('All Files',
        #                                                   '*.*')))
        # --- End Equivalence ---
        kwargs = {'initialdir': 'C:\\',
                  'title': 'Select File',
                  'filetypes': (('Text Files', '.txt'),
                                ('All Files', '*.*'))}
        filename = filedialog.askopenfilename(**kwargs)
        with open(filename, 'r') as inp:
            self.textEditor.insert(tk.END, inp.read())


rt = tk.Tk()
rt.title('"Save File" Dialog Example')
rt.geometry("450x350+350+250")
app = SaveFileDialog(rt)
rt.mainloop()
