# -*- coding: utf-8 -*-

import callback_functions as cf

# Tkinter imports
import tkinter as tk
from tkinter import ttk


class guiTextLabel():
    def __init__(gui, parent, style, **kwargs):
        gui.text = tk.StringVar(parent, '')

        gui.labelKwargs, gui.showKwargs = splitKwargs(**kwargs)

        gui.label = tk.Label(parent, **gui.labelKwargs,
                              textvariable=gui.text)

        if 'text' in gui.labelKwargs:
            gui.text.set(gui.labelKwargs['text'])

        gui.show = gui._pack if style == 'pack' else gui._grid
        gui.hide = gui._pack_forget if style == 'pack' else gui._grid_forget

    def _pack(gui, text=None):
        noText = {k: v for (k, v) in gui.showKwargs.items() if k != 'text'}

        gui.label.pack(**noText)
        if text is not None:
            gui.set(text)
        elif 'text' in gui.labelKwargs:
            gui.set(gui.labelKwargs['text'])

    def _pack_forget(gui,):
        gui.label.pack_forget()

    def _grid(gui, text=None):
        gui.label.grid(**gui.showKwargs)
        if text is not None:
            gui.set(text)

    def _grid_forgt(gui):
        gui.label.grid_forget()

    def set(gui, newText):
        gui.text.set(newText)

    def get(gui,):
        gui.text.get()


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


def buildXYZMinMaxModifiers(gui, parent, ):

    limitskwargs = {'width': 8, 'validate': "key"}

    # - - - - - - - - - -
    # Row 0 - X Min/Max
    gui.xLimitsRow = 0
    gui.xLimits = tk.BooleanVar(value=False)

    # Checkbox for turning on limit setting
    gui.xLimitsBox = tk.Checkbutton(
                            parent,
                            text='X ',
                            variable=gui.xLimits,
                            command=lambda: cf.showHideXLimits(gui))
    gui.xLimitsBox.grid(row=gui.xLimitsRow, column=0, sticky=tk.W)

    # Entry for minimum Y value
    gui.xMin = tk.StringVar()
    gui.xMinEntry = tk.Entry(parent, **limitskwargs)
    gui.xMinEntry['textvariable'] = gui.xMin
    gui.xMinEntry.insert(0, 'Min')
    gui.xMinEntry.bind('<Key>', gui.waitToPlot)
    gui.xMinEntry.bind("<FocusIn>",
                        lambda _: cf.modifyLimitsEntry(gui, _, 'xMin'))
    gui.xMinEntry.bind("<FocusOut>",
                        lambda _: cf.modifyLimitsEntry(gui, _, 'xMin'))

    # Entry for maximum Y value
    gui.xMax = tk.StringVar()
    gui.xMaxEntry = tk.Entry(parent, **limitskwargs)
    gui.xMaxEntry['textvariable'] = gui.xMax
    gui.xMaxEntry.insert(0, 'Max')
    gui.xMaxEntry.bind('<Key>', gui.waitToPlot)
    gui.xMaxEntry.bind("<FocusIn>",
                        lambda _: cf.modifyLimitsEntry(gui, _, 'xMax'))
    gui.xMaxEntry.bind("<FocusOut>",
                        lambda _: cf.modifyLimitsEntry(gui, _, 'xMax'))

    # - - - - - - - - - -
    # Row 1 - Y Min/Max
    gui.yLimitsRow = 1
    gui.yLimits = tk.BooleanVar(value=False)

    # Checkbox for turning on limit setting
    gui.yLimitsBox = tk.Checkbutton(
                            parent,
                            text='Y ',
                            variable=gui.yLimits,
                            command=lambda: cf.showHideYLimits(gui))
    gui.yLimitsBox.grid(row=gui.yLimitsRow, column=0, sticky=tk.W)

    # Entry for minimum Y value
    gui.yMin = tk.StringVar()
    gui.yMinEntry = tk.Entry(parent, **limitskwargs)
    gui.yMinEntry['textvariable'] = gui.yMin
    gui.yMinEntry.insert(0, 'Min')
    gui.yMinEntry.bind('<Key>', gui.waitToPlot)
    gui.yMinEntry.bind("<FocusIn>",
                        lambda _: cf.modifyLimitsEntry(gui, _, 'yMin'))
    gui.yMinEntry.bind("<FocusOut>",
                        lambda _: cf.modifyLimitsEntry(gui, _, 'yMin'))

    # Entry for maximum Y value
    gui.yMax = tk.StringVar()
    gui.yMaxEntry = tk.Entry(parent, **limitskwargs)
    gui.yMaxEntry['textvariable'] = gui.yMax
    gui.yMaxEntry.insert(0, 'Max')
    gui.yMaxEntry.bind('<Key>', gui.waitToPlot)
    gui.yMaxEntry.bind("<FocusOut>",
                        lambda _: cf.modifyLimitsEntry(gui, _, 'yMax'))
    gui.yMaxEntry.bind("<FocusIn>",
                        lambda _: cf.modifyLimitsEntry(gui, _, 'yMax'))

    # - - - - - - - - - -
    # Row 2 - Z Min/Max
    gui.zLimitsRow = 2
    gui.zLimits = tk.BooleanVar(value=False)

    # Checkbox for turning on limit setting
    gui.zLimitsBox = tk.Checkbutton(
                            parent,
                            text='Z ',
                            variable=gui.zLimits,
                            command=lambda: cf.showHideZLimits(gui))
    gui.zLimitsBox.grid(row=gui.zLimitsRow, column=0, sticky=tk.W)

    # Entry for minimum Z value
    gui.zMin = tk.StringVar()
    gui.zMinEntry = tk.Entry(parent, **limitskwargs)
    gui.zMinEntry['textvariable'] = gui.zMin
    gui.zMinEntry.insert(0, 'Min')
    gui.zMinEntry.bind('<Key>', gui.waitToPlot)
    gui.zMinEntry.bind("<FocusIn>",
                        lambda _: cf.modifyLimitsEntry(gui, _, 'zMin'))
    gui.zMinEntry.bind("<FocusOut>",
                        lambda _: cf.modifyLimitsEntry(gui, _, 'zMin'))

    # Entry for maximum Z value
    gui.zMax = tk.StringVar()
    gui.zMaxEntry = tk.Entry(parent, **limitskwargs)
    gui.zMaxEntry['textvariable'] = gui.zMax
    gui.zMaxEntry.insert(0, 'Max')
    gui.zMaxEntry.bind('<Key>', gui.waitToPlot)
    gui.zMaxEntry.bind("<FocusIn>",
                        lambda _: cf.modifyLimitsEntry(gui, _, 'zMax'))
    gui.zMaxEntry.bind("<FocusOut>",
                        lambda _: cf.modifyLimitsEntry(gui, _, 'zMax'))