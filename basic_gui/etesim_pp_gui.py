# -*- coding: utf-8 -*-

# Module-Level Imports
import os
import platform
import numpy as np
import tkinter as tk
from tkinter import messagebox as mb
from tkinter import ttk
from tkinter import filedialog
import tkinter.font as font
import tkinter.colorchooser as tkColorChooser
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# The original function was deprecated so we're importing the new one
# to match tutorials more closely
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
# from matplotlib.figure import Figure

# Imports and settings for Tkinter
import matplotlib
matplotlib.use("TkAgg")  # To use with Tkinter

# TODO List ---------------------------------------->
#
# (High)
#   [x] Grid option
#       -> Bug: Creates screen trash for 3D plots
#   [x] X/Y/Z Labels (Checkbox for each)
#   [ ] Add color options for graph lines
#   [ ] Add option to graph assets (radars/etc.)
#
# (Low)
#   [ ] Add ability to place multiple graphs at once
#   [ ] Add CheckBox for ax.show_legend()
#   [ ] Split up graph styles across two lines
#   [ ] Place X/Y/Z Drop-downs in a LabelFrame
#   [ ] Add option for legend
#   [ ] Add button to render graph manually
#   [ ] Add font-family option for labels/titles
#   [ ] Add underline option for labels/titles
# -------------------------------------------------->


class SimpleGUI(tk.Tk):
    def __init__(self, *args, **kwargs):

        # initializing and adding a GUI icon and title
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.iconbitmap(self, default="images/window_icon_radar.ico")
        tk.Tk.wm_title(self, "ETESim Plotting Suite")
        self.geometry("850x550+150+50")

        # Waiting for user to stop typing
        self._after_id = None

        # We need to set some sample values for the GUI not to crash
        self.plotCols = ['']
        self.dimensions = 2
        self.x = []
        self.y = []
        self.z = []
        self.missileDF = pd.DataFrame({' ': []})
        self.toolbar = None
        self.figure = None
        self.canvas = None
        self.titleColorRGB = (0, 0, 0)
        self.titleColorHex = tk.StringVar(value='#000000')
        self.plotColorRGB = (31, 119, 180)
        self.plotColorHex = tk.StringVar(value='#1f77b4')

        # Creating a Notebook seems to be the key to making tabs
        # build_tabs() compartmentalizes the code for making the tabs
        self.tabs = ttk.Notebook(self,
                                 height=self.winfo_reqheight(),
                                 width=self.winfo_reqwidth())
        self.build_tabs(self.tabs)
        self.tabs.pack(fill=tk.BOTH)
        self.tabs.bind("<Configure>", self.autosizer)

        self.statusBar = ttk.Frame(self, height=100)
        self.statusBar.pack(side=tk.BOTTOM)
        self.status = tk.Label(self.statusBar, text="on the way…", bd=1,
                               relief=tk.SUNKEN, height=1)
        self.status.pack(fill=tk.BOTH)

    def build_tabs(self, parent):
        """ A constructor for the tabbed layout of the UI """

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Tab 1: Data Input
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.inputTab = ttk.Frame(parent,)
        self.datainput_icon = tk.PhotoImage(file='images/input-data-1.png')
        parent.add(self.inputTab,
                   text='Data Input',
                   image=self.datainput_icon,
                   compound=tk.LEFT,)

        # - - - - - - - - - - - - - - - -
        # Row 0 - Browsing for Directory
        self.topDirLabel = tk.Label(self.inputTab,
                                    text='Directory with Run(s): ')
        self.topDirLabel.grid(row=0, sticky=tk.W)

        # TODO: Change this back to empty string
        self.topDir = os.getcwd()
        self.topDirPath = tk.Text(self.inputTab, relief=tk.SUNKEN)
        self.topDirPath.insert(tk.INSERT, self.topDir)
        self.topDirPath.config(width=40, height=1.45)
        self.topDirPath.grid(row=0, column=1, columnspan=5, sticky=tk.W)

        self.topDirBrowseButton = tk.Button(self.inputTab,
                                            text='Browse',
                                            height=1,
                                            command=self.getTopDir)
        self.topDirBrowseButton.grid(row=0, column=6, padx=4)

        self.topDirLoadButton = tk.Button(self.inputTab,
                                          text='Load',
                                          height=1,
                                          command=self.loadFromTopDir)
        self.topDirLoadButton.grid(row=0, column=7, padx=4)

        # - - - - - - - - - - - - - - - -
        # Row 1 - Threat Type(s)
        self.threatTypeOptions = ('Infer', 'ABT', 'TBM')
        self.threatTypeLabel = tk.Label(self.inputTab, text='Threat: ')
        self.threatTypeLabel.grid(row=1, sticky=tk.W)
        self.threatType = tk.StringVar()
        self.threatTypeCB = ttk.Combobox(self.inputTab,
                                         textvariable=self.threatType,
                                         values=self.threatTypeOptions,
                                         state='readonly',
                                         width=20,)

        self.threatTypeCB.set('Infer')  # Could use .current(0)
        self.threatTypeCB.grid(row=1, column=1, columnspan=2)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Tab 2: Save Options
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.saveOptionsIcon = tk.PhotoImage(file='images/save-disk.png')
        self.saveOptionsTab = ttk.Frame(parent,)
        saveOptions_kwargs = {'text': 'Saving Options',
                              'image': self.saveOptionsIcon,
                              'compound': tk.LEFT, }
        assert(saveOptions_kwargs)  # Remove if uncommenting below line
        # parent.add(self.saveOptionsTab, **saveOptions_kwargs)

        # - - - - - - - - - - - - - - - -
        # Row 0 - Output Directory
        self.outDirLabel = tk.Label(self.saveOptionsTab,
                                    text='Output Directory: ')
        self.outDirLabel.grid(row=0, sticky=tk.W)

        self.outDirPath = tk.Text(self.saveOptionsTab, relief=tk.SUNKEN)
        self.outDirPath.config(width=40, height=1.45)
        self.outDirPath.grid(row=0, column=1, columnspan=5, sticky=tk.W)

        self.outDirBrowseButton = tk.Button(self.saveOptionsTab,
                                            text='Browse',
                                            height=1,
                                            command=self.getOutDir)
        self.outDirBrowseButton.grid(row=0, column=6, padx=4)

        # - - - - - - - - - - - - - - - -
        # Row 1 - Image Save Type
        self.imageTypeOptions = ('JPG', 'PDF', 'PNG', 'TIFF')
        self.imageTypeLabel = tk.Label(self.saveOptionsTab,
                                       text='Image Format: ')
        self.imageTypeLabel.grid(row=1, sticky=tk.W)
        self.imageType = tk.StringVar()

        self.imageTypeCB = ttk.Combobox(self.saveOptionsTab,
                                        textvariable=self.imageType,
                                        values=self.imageTypeOptions,
                                        state='disabled',
                                        width=20,)

        # Sets the default to PNG since it looks nice and is small
        self.imageTypeCB.set('PNG')
        self.imageTypeCB.grid(row=1, column=1, columnspan=2)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Tab 3: Graph Options
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        gs_ico = 'images/graph-settings-icon.png'
        self.graphOptionsIcon = tk.PhotoImage(file=gs_ico)
        self.graphOptionsTab = ttk.Frame(parent,)
        graphOpts_kwargs = {'text': 'Graph Options',
                            'image': self.graphOptionsIcon,
                            'compound': tk.LEFT, }
        assert(graphOpts_kwargs)  # Remove if uncommenting below line
        # parent.add(self.graphOptionsTab, **graphOpts_kwargs)

        # - - - - - - - - - - - - - - - -
        # Row 0 - Number of Plots
        thisrow = 0
        # Setting up a 'spinbox' where you can only select a range of values
        self.numPlots = tk.IntVar(self.graphOptionsTab, 1)
        self.numPlotsLabel = ttk.Label(self.graphOptionsTab,
                                       text='Simultaneous Plots: ')
        self.numPlotsLabel.grid(row=thisrow, column=0, padx=(0, 10))

        # This can be done with tk or ttk
        # If using tk, the default value is from_ or use the "value" keyword
        # If using ttk, you have to set the default value with .set()
        self.numPlotsSpinBox = ttk.Spinbox(self.graphOptionsTab,
                                           from_=1,
                                           to=5,
                                           command=self.setNumPlots,
                                           width=3,
                                           state='readonly',)  # to limit input
        self.numPlotsSpinBox.insert(0, '1')
        self.numPlotsSpinBox.grid(row=thisrow, column=1)
        self.numPlotsSpinBox.set('1')

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Tab 4: Viewer
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.viewer_icon = tk.PhotoImage(file='images/three-dim-graph.png')
        self.viewerTab = ttk.Frame(parent,)
        parent.add(
                self.viewerTab,
                text='Viewer',
                image=self.viewer_icon,   # The icon feature is awesome
                compound=tk.LEFT,)        # Places icon left of text

        self.graphPanes = ttk.Panedwindow(self.viewerTab, orient=tk.HORIZONTAL)
        self.graphPanes.pack(fill=tk.BOTH, expand=True)

        # - - - - - - - - - - - - - - - -
        # Defining Edit and View Panes
        self.editPane = ttk.Frame(self.graphPanes, width=250, relief=tk.GROOVE)
        self.graphPanes.add(self.editPane)

        # We don't want the edit frame to automatically resize
        self.editPane.grid_propagate(0)
        self.viewPane = ttk.Frame(self.graphPanes,)
        self.graphPanes.add(self.viewPane)

        # - - - - - - - - - - - - - - - -
        # Row 0 - X Plot Column
        thisrow = 0
        self.xCol = tk.StringVar()
        self.xLabel = tk.Label(self.editPane, text='X=')
        self.xLabel.grid(row=thisrow, column=0, sticky=tk.W,
                         padx=(2, 0), pady=(2, 0))
        self.xCB = ttk.Combobox(self.editPane, textvariable=self.xCol,
                                values=self.plotCols, state='readonly',
                                width=30)
        self.xCB.grid(row=thisrow, column=1)
        self.xCB.bind('<<ComboboxSelected>>', self.showPlot)

        # - - - - - - - - - - - - - - - -
        # Row 1 - Y Plot Column
        thisrow += 1
        self.yCol = tk.StringVar()
        self.yLabel = tk.Label(self.editPane, text='Y=')
        self.yLabel.grid(row=thisrow, column=0, sticky=tk.W, padx=(2, 0),)
        self.yCB = ttk.Combobox(self.editPane, textvariable=self.yCol,
                                values=self.plotCols, state='readonly',
                                width=30)
        self.yCB.grid(row=thisrow, column=1)
        self.yCB.bind('<<ComboboxSelected>>', self.showPlot)

        # - - - - - - - - - - - - - - - -
        # Row 2 - Z Plot Column
        thisrow += 1
        self.zCol = tk.StringVar()
        self.zLabel = tk.Label(self.editPane, text='Z=')
        self.zLabel.grid(row=thisrow, column=0, sticky=tk.W, padx=(2, 0),)
        self.zCB = ttk.Combobox(self.editPane, textvariable=self.zCol,
                                values=self.plotCols, state='readonly',
                                width=30)
        self.zCB.grid(row=thisrow, column=1)
        self.zCB.bind('<<ComboboxSelected>>', self.showPlot)

        # - - - - - - - - - - - - - - - -
        # Row 3 - XYZ Min/Max Fields
        thisrow += 1
        self.xyzMinMaxFrame = ttk.LabelFrame(self.editPane,
                                             text="Set Limits",
                                             relief=tk.RIDGE)
        self.xyzMinMaxFrame.grid(row=thisrow, column=1, sticky=tk.W, pady=3,)
        limitskwargs = {'width': 8, 'validate': "key"}

        # - - - - - - - - - -
        # Row 3.0 - X Min/Max
        self.xLimitsRow = 0
        self.xLimits = tk.BooleanVar(value=False)

        # Checkbox for turning on limit setting
        self.xLimitsBox = tk.Checkbutton(self.xyzMinMaxFrame,
                                         text='X ',
                                         variable=self.xLimits,
                                         command=self.showHideXLimits)
        self.xLimitsBox.grid(row=self.xLimitsRow, column=0, sticky=tk.W)

        # Entry for minimum Y value
        self.xMin = tk.StringVar()
        self.xMinEntry = tk.Entry(self.xyzMinMaxFrame, **limitskwargs)
        self.xMinEntry['textvariable'] = self.xMin
        self.xMinEntry.insert(0, 'Min')
        self.xMinEntry.bind('<Key>', self.handle_wait)
        self.xMinEntry.bind("<FocusIn>",
                            lambda _: self.modifyLimitsEntry(_, 'xMin'))
        self.xMinEntry.bind("<FocusOut>",
                            lambda _: self.modifyLimitsEntry(_, 'xMin'))

        # Entry for maximum Y value
        self.xMax = tk.StringVar()
        self.xMaxEntry = tk.Entry(self.xyzMinMaxFrame, **limitskwargs)
        self.xMaxEntry['textvariable'] = self.xMax
        self.xMaxEntry.insert(0, 'Max')
        self.xMaxEntry.bind('<Key>', self.handle_wait)
        self.xMaxEntry.bind("<FocusIn>",
                            lambda _: self.modifyLimitsEntry(_, 'xMax'))
        self.xMaxEntry.bind("<FocusOut>",
                            lambda _: self.modifyLimitsEntry(_, 'xMax'))

        # - - - - - - - - - -
        # Row 3.1 - Y Min/Max
        self.yLimitsRow = 1
        self.yLimits = tk.BooleanVar(value=False)

        # Checkbox for turning on limit setting
        self.yLimitsBox = tk.Checkbutton(self.xyzMinMaxFrame,
                                         text='Y ',
                                         variable=self.yLimits,
                                         command=self.showHideYLimits)
        self.yLimitsBox.grid(row=self.yLimitsRow, column=0, sticky=tk.W)

        # Entry for minimum Y value
        self.yMin = tk.StringVar()
        self.yMinEntry = tk.Entry(self.xyzMinMaxFrame, **limitskwargs)
        self.yMinEntry['textvariable'] = self.yMin
        self.yMinEntry.insert(0, 'Min')
        self.yMinEntry.bind('<Key>', self.handle_wait)
        self.yMinEntry.bind("<FocusIn>",
                            lambda _: self.modifyLimitsEntry(_, 'yMin'))
        self.yMinEntry.bind("<FocusOut>",
                            lambda _: self.modifyLimitsEntry(_, 'yMin'))

        # Entry for maximum Y value
        self.yMax = tk.StringVar()
        self.yMaxEntry = tk.Entry(self.xyzMinMaxFrame, **limitskwargs)
        self.yMaxEntry['textvariable'] = self.yMax
        self.yMaxEntry.insert(0, 'Max')
        self.yMaxEntry.bind('<Key>', self.handle_wait)
        self.yMaxEntry.bind("<FocusOut>",
                            lambda _: self.modifyLimitsEntry(_, 'yMax'))
        self.yMaxEntry.bind("<FocusIn>",
                            lambda _: self.modifyLimitsEntry(_, 'yMax'))

        # - - - - - - - - - -
        # Row 3.2 - Z Min/Max
        self.zLimitsRow = 2
        self.zLimits = tk.BooleanVar(value=False)

        # Checkbox for turning on limit setting
        self.zLimitsBox = tk.Checkbutton(self.xyzMinMaxFrame,
                                         text='Z ',
                                         variable=self.zLimits,
                                         command=self.showHideZLimits)
        self.zLimitsBox.grid(row=self.zLimitsRow, column=0, sticky=tk.W)

        # Entry for minimum Z value
        self.zMin = tk.StringVar()
        self.zMinEntry = tk.Entry(self.xyzMinMaxFrame, **limitskwargs)
        self.zMinEntry['textvariable'] = self.zMin
        self.zMinEntry.insert(0, 'Min')
        self.zMinEntry.bind('<Key>', self.handle_wait)
        self.zMinEntry.bind("<FocusIn>",
                            lambda _: self.modifyLimitsEntry(_, 'zMin'))
        self.zMinEntry.bind("<FocusOut>",
                            lambda _: self.modifyLimitsEntry(_, 'zMin'))

        # Entry for maximum Z value
        self.zMax = tk.StringVar()
        self.zMaxEntry = tk.Entry(self.xyzMinMaxFrame, **limitskwargs)
        self.zMaxEntry['textvariable'] = self.zMax
        self.zMaxEntry.insert(0, 'Max')
        self.zMaxEntry.bind('<Key>', self.handle_wait)
        self.zMaxEntry.bind("<FocusIn>",
                            lambda _: self.modifyLimitsEntry(_, 'zMax'))
        self.zMaxEntry.bind("<FocusOut>",
                            lambda _: self.modifyLimitsEntry(_, 'zMax'))

        # - - - - - - - - - - - - - - - -
        # Row 4 - Custom Title
        thisrow += 1
        self.titleLF = ttk.LabelFrame(self.editPane, text="Custom Title",
                                      relief=tk.RIDGE)
        self.titleLF.grid(row=thisrow, column=1, sticky=tk.W, pady=3)

        # - - - - - - - - - -
        # Row 4.0 - Text
        self.titleText = tk.StringVar()
        titlekwargs = {'width': 35, 'textvariable': self.titleText, }
        self.titleEntry = ttk.Entry(self.titleLF, **titlekwargs)
        self.titleEntry.insert(0, '')

        # Adds a waiting period for the user to stop typing
        self.titleEntry.bind('<Key>', self.handle_wait)
        self.titleEntry.grid(row=0, column=0, sticky=tk.W, columnspan=5)

        # - - - - - - - - - -
        # Row 4.1 - Styling
        self.titleSize = ttk.Spinbox(self.titleLF, from_=0, to=32, width=3,
                                     command=lambda: self.showPlot(1))
        self.titleSize.set('15')
        self.titleSize.grid(row=1, column=0)

        self.boldTitleOn, self.itTitleOn = (0, 0)

        # Bold button
        boldFont = font.Font(size=10, weight="bold")
        self.boldTitleButton = tk.Button(
                                self.titleLF, text="B", width=3,
                                relief=tk.FLAT,
                                font=boldFont,
                                command=lambda: self.editTitleOptions('b'),)
        self.boldTitleButton.grid(row=1, column=1,)

        # Italic button
        itFont = font.Font(size=10, slant="italic")
        self.itTitleButton = tk.Button(
                                self.titleLF, text="I", width=3,
                                relief=tk.FLAT,
                                font=itFont,
                                command=lambda: self.editTitleOptions('i'),)
        self.itTitleButton.grid(row=1, column=2,)

        # Title Color Picker
        tc_kwargs = {'width': 8, 'textvariable': self.titleColorHex, }
        self.titleColorEntry = ttk.Entry(self.titleLF, **tc_kwargs)

        # Adds a waiting period for the user to stop typing
        self.titleColorEntry.bind('<Key>', self.handle_wait)
        self.titleColorEntry.grid(row=1, column=3, sticky=tk.W)

        # Setting up color wheel buttong
        self.titleColorWheel = tk.PhotoImage(file='images/color_wheel.png')
        self.titleColorButton = tk.Button(self.titleLF,
                                          image=self.titleColorWheel,
                                          command=self.pickTitleColor)
        self.titleColorButton.grid(row=1, column=4,)

        # - - - - - - - - - - - - - - - -
        # Row 5 - Style Options
        thisrow += 1

        self.styleLF = ttk.LabelFrame(self.editPane, text="Style",
                                      relief=tk.RIDGE)
        self.styleLF.grid(row=thisrow, column=1, sticky=tk.W, pady=3)

        self.plotStyle = tk.StringVar(self.styleLF, 'line')

        linekwargs = {'text': 'Line', 'var': self.plotStyle,
                      'value': 'line', 'command': self.setPlotStyleOptions, }

        scatterkwargs = {'text': 'Scatter', 'var': self.plotStyle,
                         'value': 'scatter',
                         'command': self.setPlotStyleOptions, }

        self.lineOn = ttk.Radiobutton(self.styleLF, **linekwargs,)
        self.scatterOn = ttk.Radiobutton(self.styleLF, **scatterkwargs)

        # Setting up a CB to be placed beside Line Style radio button
        self.lineStyleOptions = ('-', '--', ':', '-.', )
        self.lineStyle = tk.StringVar(self.styleLF, '-')
        lineStyle_kwargs = {'textvariable': self.lineStyle,
                            'values': self.lineStyleOptions,
                            'state': 'readonly',
                            'width': 4}
        self.lineStyleCB = ttk.Combobox(self.styleLF, **lineStyle_kwargs)

        # Setting up a CB to be placed beside Scatter Style radio button
        self.scatterStyleOptions = ('o', 'v', '^', '<', '>', '8', 's', 'p',
                                    '*', 'h', 'H', 'D', 'd', 'P', 'X')
        self.scatterStyle = tk.StringVar(self.graphOptionsTab, 'o')

        scatterStyle_kwargs = {'textvariable': self.scatterStyle,
                               'values': self.scatterStyleOptions,
                               'state': 'disabled',
                               'width': 4}

        self.scatterStyleCB = ttk.Combobox(self.styleLF,
                                           **scatterStyle_kwargs)

        self.lineOn.grid(row=0, column=0, padx=(0, 0))
        self.lineStyleCB.grid(row=0, column=1)
        self.lineStyleCB.bind('<<ComboboxSelected>>', self.showPlot)
        self.scatterOn.grid(row=0, column=2, padx=(10, 0))
        self.scatterStyleCB.grid(row=0, column=3)
        self.scatterStyleCB.bind('<<ComboboxSelected>>', self.showPlot)

        # - - - - - - - - - -
        # Row 5.0 - Plot Color
        self.plotColorFrame = tk.Frame(self.styleLF)
        self.plotColorFrame.grid(row=1, column=0, columnspan=4)

        self.plotColorLabel = ttk.Label(self.plotColorFrame,
                                        text='Plot Color:')
        self.plotColorLabel.grid(row=0, column=0, sticky=tk.W)

        # Plot Color Picker
        pc_kwargs = {'width': 20, 'textvariable': self.plotColorHex, }
        self.plotColorEntry = ttk.Entry(self.plotColorFrame, **pc_kwargs)

        # Adds a waiting period for the user to stop typing
        self.plotColorEntry.bind('<Key>', self.handle_wait)
        self.plotColorEntry.grid(row=0, column=1, sticky=tk.E, pady=3)

        # Setting up color wheel buttong
        self.plotColorWheel = tk.PhotoImage(file='images/color_wheel.png')
        self.plotColorButton = tk.Button(self.plotColorFrame,
                                         image=self.plotColorWheel,
                                         command=self.pickPlotColor)
        self.plotColorButton.grid(row=0, column=2, sticky=tk.E, pady=3)

        # - - - - - - - - - - - - - - - -
        # Row 6 - Additional Options
        thisrow += 1
        self.addOptsLF = ttk.LabelFrame(self.editPane, relief=tk.RIDGE,
                                        text="Additional Options",)
        self.addOptsLF.grid(row=thisrow, column=1, sticky=tk.W, pady=3,)

        # - - - - - - - - - -
        # Row 6.0 - Grid
        self.gridLabel = ttk.Label(self.addOptsLF, text='Gridlines:',)
        self.gridLabel.grid(row=0, column=0, sticky=tk.W, padx=(0, 2))

        self.gridMajor = tk.BooleanVar(value=True)
        self.gridMinor = tk.BooleanVar(value=False)

        gmaj_kwargs = {'text': 'Major', 'variable': self.gridMajor,
                       'command': lambda: self.showPlot(1), }
        gmin_kwargs = {'text': 'Minor', 'variable': self.gridMinor,
                       'command': lambda: self.showPlot(1), }

        self.gridMajorCB = tk.Checkbutton(self.addOptsLF, **gmaj_kwargs)
        self.gridMajorCB.grid(row=0, column=1, sticky=tk.W,)

        self.gridMinorCB = tk.Checkbutton(self.addOptsLF, **gmin_kwargs)
        self.gridMinorCB.grid(row=0, column=2, sticky=tk.W,)

        # - - - - - - - - - -
        # Row 6.1 - Labels
        self.showAxLabel = ttk.Label(self.addOptsLF, text='Axis Labels:',)
        self.showAxLabel.grid(row=1, column=0, sticky=tk.W, padx=(0, 2))
        self.showAxFrame = tk.Frame(self.addOptsLF)
        self.showAxFrame.grid(row=1, column=1, sticky=tk.W, columnspan=2)

        # - - - - - - - - - -
        # Row 6.1.0 - XYZ
        self.showXLabel = tk.BooleanVar(value=True)
        self.showYLabel = tk.BooleanVar(value=True)
        self.showZLabel = tk.BooleanVar(value=True)
        xlbl_kwargs = {'text': 'X', 'variable': self.showXLabel,
                       'command': lambda: self.showPlot(1), }
        ylbl_kwargs = {'text': 'Y', 'variable': self.showYLabel,
                       'command': lambda: self.showPlot(1), }
        zlbl_kwargs = {'text': 'Z', 'variable': self.showZLabel,
                       'command': lambda: self.showPlot(1), }

        self.showXLabelCB = tk.Checkbutton(self.showAxFrame, **xlbl_kwargs)
        self.showXLabelCB.grid(row=0, column=0, sticky=tk.W)
        self.showYLabelCB = tk.Checkbutton(self.showAxFrame, **ylbl_kwargs)
        self.showYLabelCB.grid(row=0, column=1, sticky=tk.W)
        self.showZLabelCB = tk.Checkbutton(self.showAxFrame, **zlbl_kwargs)
        self.showZLabelCB.grid(row=0, column=2, sticky=tk.W)

    ####################################################################
    # Callback functions
    ####################################################################
    def modifyLimitsEntry(self, event, entry=None):
        focusIn = 9
        focusOut = 10
        evType = int(event.type._value_)

        # On focusIn events, if the value says Min or Max, delete it
        if evType == focusIn:
            if entry == 'xMin':
                if self.xMinEntry.get() == 'Min':
                    self.xMinEntry.delete(0, tk.END)
            elif entry == 'xMax':
                if self.xMaxEntry.get() == 'Max':
                    self.xMaxEntry.delete(0, tk.END)
            elif entry == 'yMin':
                if self.yMinEntry.get() == 'Min':
                    self.yMinEntry.delete(0, tk.END)
            elif entry == 'yMax':
                if self.yMaxEntry.get() == 'Max':
                    self.yMaxEntry.delete(0, tk.END)
            elif entry == 'zMin':
                if self.zMinEntry.get() == 'Min':
                    self.zMinEntry.delete(0, tk.END)
            elif entry == 'zMax':
                if self.zMaxEntry.get() == 'Max':
                    self.zMaxEntry.delete(0, tk.END)

        # On focusOut events, if the entry isn't a valid floating
        # point number, then put Min/Max back in where it should be
        elif evType == focusOut:
            if entry == 'xMin':
                try:
                    float(self.xMinEntry.get())
                except ValueError as ve:
                    assert(ve)
                    self.xMinEntry.delete(0, tk.END)
                    self.xMinEntry.insert(0, 'Min')
            elif entry == 'xMax':
                try:
                    float(self.xMaxEntry.get())
                except ValueError as ve:
                    assert(ve)
                    self.xMaxEntry.delete(0, tk.END)
                    self.xMaxEntry.insert(0, 'Max')
            elif entry == 'yMin':
                try:
                    float(self.yMinEntry.get())
                except ValueError as ve:
                    assert(ve)
                    self.yMinEntry.delete(0, tk.END)
                    self.yMinEntry.insert(0, 'Min')
            elif entry == 'yMax':
                try:
                    float(self.yMaxEntry.get())
                except ValueError as ve:
                    assert(ve)
                    self.yMaxEntry.delete(0, tk.END)
                    self.yMaxEntry.insert(0, 'Max')
            elif entry == 'zMin':
                try:
                    float(self.zMinEntry.get())
                except ValueError as ve:
                    assert(ve)
                    self.zMinEntry.delete(0, tk.END)
                    self.zMinEntry.insert(0, 'Min')
            elif entry == 'zMax':
                try:
                    float(self.zMaxEntry.get())
                except ValueError as ve:
                    assert(ve)
                    self.zMaxEntry.delete(0, tk.END)
                    self.zMaxEntry.insert(0, 'Max')

    def editTitleOptions(self, event=None):
        # Reading events
        if event == 'b':  # Swapping bold press state
            self.boldTitleOn = not self.boldTitleOn
        elif event == 'i':  # Swapping italic press state
            self.itTitleOn = not self.itTitleOn

        # Updating button behavior
        br = tk.SUNKEN if self.boldTitleOn else tk.FLAT
        ir = tk.SUNKEN if self.itTitleOn else tk.FLAT
        self.boldTitleButton.config(relief=br)
        self.itTitleButton.config(relief=ir)
        self.showPlot(1)

    def pickTitleColor(self):
        color = tkColorChooser.askcolor(color=self.titleColorRGB)
        if None not in color:
            self.titleColorHex.set(color[1])
            self.titleColorRGB = self.hex2rgb(self.titleColorHex.get())
            self.editTitleOptions(self.titleColorHex.get())

    def pickPlotColor(self):
        color = tkColorChooser.askcolor(color=self.plotColorRGB)
        if None not in color:
            self.plotColorHex.set(color[1])
            self.plotColorRGB = self.hex2rgb(self.plotColorHex.get())
            self.showPlot(1)

    def setVals(self):
        """ Loading x/y/z values from the DataFrame for plotting
            if the user has selected an option from the drop-down menu.
        """

        # Setting graph dimensions based upon Z setting and
        # loading values from DataFrame
        if self.zCol.get() == '':
            self.dimensions = 2
            self.z = []
        else:
            self.dimensions = 3
            self.z = self.missileDF[self.zCol.get()].values

        # Pulling x/y values from the DataFrame
        if (self.xCol.get() == '') or (self.yCol.get() == ''):
            self.x, self.y, self.z = [], [], []
        else:
            self.x = self.missileDF[self.xCol.get()].values
            self.y = self.missileDF[self.yCol.get()].values

    def getTopDir(self):
        """
        Opens a file browswer for the run files. Once selected,
        the chosen file path will show in the text field.
        The path can be typed in also.
        ** Only a directory can be selected
        """

        kwargs = {'title': 'Select Directory Containing Run(s)',
                  'initialdir': self.default_path(),
                  'mustexist': True, }
        self.topDir = filedialog.askdirectory(**kwargs)
        if self.topDir != '':
            self.topDir = os.path.abspath(self.topDir)

        # Updates text widget with path (deletes old path)
        self.topDirPath.delete('1.0', tk.END)
        self.topDirPath.insert(1.0, self.topDir)

    def loadFromTopDir(self):
        # If the entry is not a valid directory, display a warning
        # message to the user
        if not os.path.isdir(self.topDir):
            mb.showinfo('Invalid directory',                 # title
                        'Please choose a valid directory!',  # message
                        icon='warning',)
            return
        self.setMissileFile()

    def setMissileFile(self):
        mfile = os.path.join(self.topDir, 'NotionalETEOutput.xlsx')
        if not os.path.isfile(mfile):
            mb.showinfo('File Not Found',                       # title
                        'No valid files found in directory!',   # message
                        icon='warning',)
            return

        # Saves the filename and reads the missile file into a DataFrame
        self.missileFile = os.path.abspath(mfile)
        self.missileDF = pd.read_excel(self.missileFile)
        self.missileDF.rename(columns=dictMap(), inplace=True)

        # Takes the columns from the DataFrame and makes them available
        # to be plotted on any axis. The first entry will be blank
        # so that users must choose to plot
        self.plotCols = [''] + sorted([col for col, val
                                       in self.missileDF.dtypes.items()
                                       if val == np.dtype('float64')])
        self.xCB['values'] = self.plotCols
        self.yCB['values'] = self.plotCols
        self.zCB['values'] = self.plotCols

    def getOutDir(self):
        """
        Opens a file browswer for the output files. Once selected,
        the chosen file path will show in the text field.
        The path can be typed in also.
        ** Only a directory can be selected
        """

        kwargs = {'title': 'Select Ouput Directory',
                  'initialdir': self.default_path(), }
        self.outDir = filedialog.askdirectory(**kwargs)
        self.outDir = os.path.abspath(self.outDir)

        # Updates text widget with path (deletes old path)
        self.outDirPath.delete('1.0', tk.END)
        self.outDirPath.insert(1.0, self.outDir)

    def setNumPlots(self):
        self.numPlots = int(self.numPlotsSpinBox.get())

    # Updates the options available based upon which radio button is selected
    def setPlotStyleOptions(self):
        if self.plotStyle.get() == 'line':
            self.lineStyleCB.config(state='readonly')
            self.scatterStyleCB.config(state='disabled')
        if self.plotStyle.get() == 'scatter':
            self.lineStyleCB.config(state='disabled')
            self.scatterStyleCB.config(state='readonly')
        self.showPlot('update')  # Need a non-None event

    def showHideXLimits(self):
        if self.xLimits.get():  # if checked
            self.xMinEntry.grid(row=self.xLimitsRow, column=2)
            self.xMaxEntry.grid(row=self.xLimitsRow, column=3)
        else:
            self.xMinEntry.grid_remove()
            self.xMaxEntry.grid_remove()
        self.showPlot(1)

    def showHideYLimits(self):
        if self.yLimits.get():  # if checked
            self.yMinEntry.grid(row=self.yLimitsRow, column=2)
            self.yMaxEntry.grid(row=self.yLimitsRow, column=3)
        else:
            self.yMinEntry.grid_remove()
            self.yMaxEntry.grid_remove()
        self.showPlot(1)

    def showHideZLimits(self):
        if self.zLimits.get():  # if checked
            self.zMinEntry.grid(row=self.zLimitsRow, column=2)
            self.zMaxEntry.grid(row=self.zLimitsRow, column=3)
        else:
            self.zMinEntry.grid_remove()
            self.zMaxEntry.grid_remove()
        self.showPlot(1)

    ####################################################################
    # Utility functions
    ####################################################################
    def default_path(self):
        defaultPaths = {'windows': 'C:\\',
                        'unix': '/',
                        'linux': '//',
                        'macos': None,
                        'sunos': None,
                        }
        thisOS = platform.system().lower()
        return defaultPaths[thisOS]

    # Creates a function that waits for an event to finish
    def handle_wait(self, event):

        # cancel the old job
        if self._after_id is not None:
            self.after_cancel(self._after_id)

        # create a new job
        self._after_id = self.after(1500, lambda: self.showPlot(event=event))

    # Adjusts the tabbed section size automatically
    def autosizer(self, event=None):
        self.tabs.config(height=self.winfo_height()-50,
                         width=self.winfo_width()-145)

    def hex2rgb(self, hexstring):
        rgb = []
        for i in range(3):
            string_ = hexstring[1 + 2 * i:1 + 2 * (i + 1)]
            rgb.append(int(f'0x0000{string_}', 0))
        return tuple(rgb)

    ####################################################################
    # Plotting function
    ####################################################################
    def showPlot(self, event=None, item=None, mode=None):

        # We want to destroy the old graph and plot on top of it
        if None not in (self.figure, self.canvas, self.toolbar):
            plt.close(self.figure)
            self.canvas.get_tk_widget().pack_forget()
            self.toolbar.pack_forget()
        self.setVals()

        # If there's no reason to update, don't update
        if event is None:
            print(event, item, mode)
            return

        # If all values are empty, then don't plot
        if len(self.x) + len(self.y) + len(self.z) == 0:
            return

        self.figure = plt.Figure()

        plot_kwargs = {}
        if self.dimensions == 3:
            plotlist = (self.x, self.y, self.z)
            plot_kwargs['projection'] = '3d'
        else:
            plotlist = (self.x, self.y)
        myplot = self.figure.add_subplot(111, **plot_kwargs)

        if self.plotStyle.get() == 'line':
            myplot.plot(*plotlist, color=self.plotColorEntry.get(),
                        linestyle=self.lineStyle.get())
        else:
            myplot.scatter(*plotlist, color=self.plotColorEntry.get(),
                           marker=self.scatterStyle.get())

        if self.titleText.get() != '':
            label = self.titleText.get()
            fontdict = {'fontsize': int(self.titleSize.get()),
                        'color': self.titleColorHex.get(),
                        'style': 'italic' if self.itTitleOn else 'normal',
                        'fontweight': 'bold' if self.boldTitleOn else 'normal'}
            myplot.set_title(label, fontdict=fontdict)

        # Adding Axes Labels
        if self.showXLabel.get():
            myplot.set_xlabel(self.xCol.get())
        if self.showYLabel.get():
            myplot.set_ylabel(self.yCol.get())
        if self.dimensions == 3 and self.showZLabel.get():
            myplot.set_zlabel(self.zCol.get())

        # Adding gridlines, if necessary
        if self.gridMajor.get():
            myplot.grid(which='major', alpha=0.8)
        if self.gridMinor.get():
            myplot.minorticks_on()
            myplot.grid(which='minor', alpha=0.2, linestyle='--',)

        # Setting the min/max values for each variable
        (xMin, xMax, yMin, yMax, zMin, zMax) = self.getLimits(myplot)
        myplot.set_xlim(xMin, xMax)
        myplot.set_ylim(yMin, yMax)
        if self.dimensions == 3:
            myplot.set_zlim(zMin, zMax)
        self.canvas = FigureCanvasTkAgg(self.figure, self.viewPane)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM,
                                         fill=tk.BOTH,
                                         expand=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.viewPane)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def getLimits(self, ax):
        xMin, xMax = ax.get_xlim()
        if self.xLimits.get():
            if self.xMin.get() not in ['', 'Min']:
                xMin = float(self.xMin.get())
            if self.xMax.get() not in ['', 'Max']:
                xMax = float(self.xMax.get())

        yMin, yMax = ax.get_ylim()
        if self.yLimits.get():
            if self.yMin.get() not in ['', 'Min']:
                yMin = float(self.yMin.get())
            if self.yMax.get() not in ['', 'Max']:
                yMax = float(self.yMax.get())

        if self.dimensions == 3:
            zMin, zMax = ax.get_zlim()
            if self.zLimits.get():
                if self.zMin.get() not in ['', 'Min']:
                    zMin = float(self.zMin.get())
                if self.zMax.get() not in ['', 'Max']:
                    zMax = float(self.zMax.get())
            return (xMin, xMax, yMin, yMax, zMin, zMax)

        return (xMin, xMax, yMin, yMax, 0, 0)


####################################################################
# Mapper for DataFrame Columns
####################################################################

def dictMap():
    dMap = {
        'uniqueid': 'Unique ID',
        'datatype': 'Data Type',
        'datarec_id': 'Data Record ID',
        'header_swmodel': 'Model',
        'time': 'Time',
        'mEast': 'Missile Position - East',
        'mNorth': 'Missile Position - North',
        'mUp': 'Missile Position - Up',
        'tEast': 'Target Position - East',
        'tNorth': 'Target Position - North',
        'tUp': 'Target Position - Up',
        }
    return dMap


def flipDict(inp):
    return {key: val for (val, key) in inp.items()}


app = SimpleGUI()
try:
    assert Axes3D  # to silence the linter
    app.mainloop()
except KeyboardInterrupt:
    app.destroy()
    print('Terminated')
