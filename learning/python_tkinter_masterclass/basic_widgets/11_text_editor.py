# -*- coding: utf-8 -*-
import tkinter as tk


root = tk.Tk()
root.geometry("450x350")


class TextEditor():
    def __init__(self, tk_root,):
        # Builds a text editor window
        self.textEditor = tk.Text(tk_root,
                                  width=30,
                                  height=10,
                                  font=('Times', 15),
                                  wrap=tk.WORD,)        # text wrapping

        self.textEditor.grid(row=0, column=0, pady=20, padx=40)

        # I'm not sure what tk.INSERT does
        # It sounds like it's basically the beginning of the field
        self.textEditor.insert(tk.INSERT,
                               'This is sample inserted text.')
        self.textEditor.config(state='normal')  # can set to "disabled"

        # This button will capture the input inside the editor
        self.printButton = tk.Button(tk_root, text='Print', width=30, height=1,
                                     command=self.consolePrint,)
        self.printButton.grid(row=3, column=0,)

    def consolePrint(self,):
        # For printing the contents of the editor to the console
        text = self.textEditor.get(1.0, tk.END)  # Why not 0?
        print(text)


app = TextEditor(root)
root.mainloop()
