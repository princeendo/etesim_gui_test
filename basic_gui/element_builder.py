# -*- coding: utf-8 -*-

# Tkinter imports
import tkinter as tk
from tkinter import ttk


class guiTextLabel():
    def __init__(self, parent, style, **kwargs):
        self.text = tk.StringVar(parent, '')

        self.labelKwargs, self.showKwargs = splitKwargs(**kwargs)

        self.label = tk.Label(parent, **self.labelKwargs,
                              textvariable=self.text)

        if 'text' in self.labelKwargs:
            self.text.set(self.labelKwargs['text'])

        self.show = self._pack if style == 'pack' else self._grid
        self.hide = self._pack_forget if style == 'pack' else self._grid_forget

    def _pack(self, text=None):
        noText = {k: v for (k, v) in self.showKwargs.items() if k != 'text'}

        self.label.pack(**noText)
        if text is not None:
            self.set(text)
        elif 'text' in self.labelKwargs:
            self.set(self.labelKwargs['text'])

    def _pack_forget(self,):
        self.label.pack_forget()

    def _grid(self, text=None):
        self.label.grid(**self.showKwargs)
        if text is not None:
            self.set(text)

    def _grid_forgt(self):
        self.label.grid_forget()

    def set(self, newText):
        self.text.set(newText)

    def get(self,):
        self.text.get()


def splitKwargs(**kwargs):
    labelOpts = {'anchor', 'bg', 'bitmap', 'bd', 'cursor', 'font', 'fg',
                 'height', 'image', 'justify', 'relief', 'text',
                 'textvariable', 'underline', 'width', 'wraplength'}

    packOpts = {'expand', 'fill', 'side'}

    gridOpts = {'column', 'columnspan', 'ipadx', 'ipady', 'padx', 'pady',
                'row', 'rowspan', 'sticky'}

    labelArgs = {}
    showArgs = {}

    for key, value in kwargs.items():
        if key in labelOpts:
            labelArgs[key] = value
        elif key in packOpts.union(gridOpts):
            showArgs[key] = value

    return labelArgs, showArgs


def buildXYZFieldSelector(gui, parent, values, plotFunc):

    # - - - - - - - - - - - - - - - -
    # Row 0 - X
    fieldRow = 0
    gui.xCol = tk.StringVar()
    gui.xLabel = tk.Label(parent, text='X=')
    gui.xLabel.grid(row=fieldRow, column=0, sticky=tk.W,
                     padx=(2, 0), pady=(2, 0))
    gui.xCB = ttk.Combobox(parent, textvariable=gui.xCol,
                            values=values, state='readonly',
                            width=30)
    gui.xCB.grid(row=fieldRow, column=1)
    gui.xCB.bind('<<ComboboxSelected>>', plotFunc)

    # - - - - - - - - - - - - - - - -
    # Row 1 - Y
    fieldRow += 1
    gui.yCol = tk.StringVar()
    gui.yLabel = tk.Label(parent, text='Y=')
    gui.yLabel.grid(row=fieldRow, column=0, sticky=tk.W, padx=(2, 0),)
    gui.yCB = ttk.Combobox(parent, textvariable=gui.yCol,
                            values=values, state='readonly',
                            width=30)
    gui.yCB.grid(row=fieldRow, column=1)
    gui.yCB.bind('<<ComboboxSelected>>', plotFunc)

    # - - - - - - - - - - - - - - - -
    # Row 2 - Z
    fieldRow += 1
    gui.zCol = tk.StringVar()
    gui.zLabel = tk.Label(parent, text='Z=')
    gui.zLabel.grid(row=fieldRow, column=0, sticky=tk.W, padx=(2, 0),)
    gui.zCB = ttk.Combobox(parent, textvariable=gui.zCol,
                            values=values, state='readonly',
                            width=30)
    gui.zCB.grid(row=fieldRow, column=1)
    gui.zCB.bind('<<ComboboxSelected>>', plotFunc)
