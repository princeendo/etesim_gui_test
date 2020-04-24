# -*- coding: utf-8 -*-

"""

This module contains a postprocessing GUI intended to generate 2D/3D
plots for various output of simulation data. Currently, it is being
designed to support ETESim output data, but will hopefully support
more datatypes in the future.

Example:
    Upon loading the the GUI with the command below, you can press the
    "Load" button on the default path and it will pull in relevant data.

        $ python etesim_pp_gui.py

Todo:
    * Add option to graph assets (radars/etc.)
    X Add ability to place multiple graphs at once
    X Add CheckBox for ax.show_legend()
    X Split up graph styles across two lines
    * Place X/Y/Z Drop-downs in a LabelFrame
    X Add option for legend
    * Add button to render graph manually
    * Add font-family option for labels/titles
    * Add underline option for labels/titles

"""

# Module-Level Imports
import os
import re
import platform
import numpy as np
import pandas as pd

# Tkinter imports
import tkinter as tk
from tkinter import messagebox as mb
from tkinter import ttk
from tkinter import filedialog
import tkinter.font as font
import tkinter.colorchooser as tkColorChooser

# matplotlib imports
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


class SimpleGUI(tk.Tk):
    """
    A subclass of tk.Tk which will serve as the main driver for the GUI.
    This GUI is intended to plot various input data from simulations,
    currently (almost) working with ETESim.

    Parameters
    ----------
    *args : standard argument list for a tk.Tk instance

    **kwargs : keyword argument list for tk.Tk instance

    Returns
    -------
    None

    """

    def __init__(self, *args, **kwargs):
        """
        The constructor function for the GUI

        Parameters
        ----------
        *args : standard argument list for a tk.Tk instance

        **kwargs : keyword argument list for tk.Tk instance

        Returns
        -------
        None

        """

        # initializing and adding a GUI icon and title
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.iconbitmap(self, default="images/window_icon_radar.ico")
        tk.Tk.wm_title(self, "ETESim Plotting Suite")
        self.geometry("850x550+150+50")

        # A temporary variable for waiting for the user to stop typing
        self._after_id = None

        # We need to set some initial values for the GUI not to crash
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
        self.plotColorRGB = (31, 119, 180)                  # matplotlib blue
        self.plotColorHex = tk.StringVar(value='#1f77b4')
        self.availableRuns = np.array([])

        # Creating a Notebook seems to be the key to making tabs
        # build_tabs() compartmentalizes the code for making the tabs
        self.tabs = ttk.Notebook(self,
                                 height=self.winfo_reqheight(),
                                 width=self.winfo_reqwidth())
        self.build_tabs(self.tabs)

        # Fills the entire GUI with the notebook and lets the GUI
        # resize the notebook as needed
        self.tabs.pack(fill=tk.BOTH)
        self.tabs.bind("<Configure>", self.autosizer)
        self.tabs.bind("<<NotebookTabChanged>>", self.setStatusBarOptions)

        # Sets up the GUI to have a status bar along the bottom
        self.statusBar = ttk.Frame(self, height=100)
        self.statusBar.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.status = tk.StringVar(self.statusBar, 'No file(s) loaded')
        self.statusLbl = tk.Label(self.statusBar, text="No file(s) loaded",
                                  relief=tk.FLAT, height=1, bd=1,
                                  textvariable=self.status)
        self.statusLbl.pack(fill=tk.BOTH, side=tk.LEFT)

        # Adds an xkcd-style Easter-Egg
        self.xkcdMode = tk.BooleanVar(value=False)
        self.xkcdModeCB = ttk.Checkbutton(self.statusBar,
                                          text='xkcd mode',
                                          variable=self.xkcdMode,
                                          command=lambda: self.startPlot(1), )
        # By default, this should not be seen on the data input tab
        self.xkcdModeCB.pack_forget()

    def build_tabs(self, parent: ttk.Notebook) -> None:
        """
        An obscenely large and not very well-organized layout
        for the tabs inside a tkinter Notebook. Is essentially a giant main().

        Parameters
        ----------
        parent : ttk.Notebook
            A tkinter object that can have tabs applied to it.

        Returns
        -------
        None

        """

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
        self.topDir = os.path.abspath(os.path.join(os.getcwd(), os.pardir,
                                                   'runs'))
        self.topDirPath = tk.Text(self.inputTab, relief=tk.SUNKEN)
        self.topDirPath.insert(tk.INSERT, self.topDir)
        self.topDirPath.config(width=60, height=1.45)
        self.topDirPath.grid(row=0, column=1, sticky=tk.W)

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
        self.threatTypeCB.grid(row=1, column=1, sticky=tk.W)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Tab 2: Viewer
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
        self.editPane = ttk.Frame(self.graphPanes, width=260, relief=tk.GROOVE)
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
        self.xCB.bind('<<ComboboxSelected>>', self.startPlot)

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
        self.yCB.bind('<<ComboboxSelected>>', self.startPlot)

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
        self.zCB.bind('<<ComboboxSelected>>', self.startPlot)

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
        self.xMinEntry.bind('<Key>', self.waitToPlot)
        self.xMinEntry.bind("<FocusIn>",
                            lambda _: self.modifyLimitsEntry(_, 'xMin'))
        self.xMinEntry.bind("<FocusOut>",
                            lambda _: self.modifyLimitsEntry(_, 'xMin'))

        # Entry for maximum Y value
        self.xMax = tk.StringVar()
        self.xMaxEntry = tk.Entry(self.xyzMinMaxFrame, **limitskwargs)
        self.xMaxEntry['textvariable'] = self.xMax
        self.xMaxEntry.insert(0, 'Max')
        self.xMaxEntry.bind('<Key>', self.waitToPlot)
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
        self.yMinEntry.bind('<Key>', self.waitToPlot)
        self.yMinEntry.bind("<FocusIn>",
                            lambda _: self.modifyLimitsEntry(_, 'yMin'))
        self.yMinEntry.bind("<FocusOut>",
                            lambda _: self.modifyLimitsEntry(_, 'yMin'))

        # Entry for maximum Y value
        self.yMax = tk.StringVar()
        self.yMaxEntry = tk.Entry(self.xyzMinMaxFrame, **limitskwargs)
        self.yMaxEntry['textvariable'] = self.yMax
        self.yMaxEntry.insert(0, 'Max')
        self.yMaxEntry.bind('<Key>', self.waitToPlot)
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
        self.zMinEntry.bind('<Key>', self.waitToPlot)
        self.zMinEntry.bind("<FocusIn>",
                            lambda _: self.modifyLimitsEntry(_, 'zMin'))
        self.zMinEntry.bind("<FocusOut>",
                            lambda _: self.modifyLimitsEntry(_, 'zMin'))

        # Entry for maximum Z value
        self.zMax = tk.StringVar()
        self.zMaxEntry = tk.Entry(self.xyzMinMaxFrame, **limitskwargs)
        self.zMaxEntry['textvariable'] = self.zMax
        self.zMaxEntry.insert(0, 'Max')
        self.zMaxEntry.bind('<Key>', self.waitToPlot)
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
        self.titleEntry.bind('<Key>', self.waitToPlot)
        self.titleEntry.grid(row=0, column=0, sticky=tk.W, columnspan=5)

        # - - - - - - - - - -
        # Row 4.1 - Styling
        self.titleSize = ttk.Spinbox(self.titleLF, from_=0, to=32, width=3,
                                     command=lambda: self.startPlot(1))
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
        self.titleColorEntry.bind('<Key>', self.waitToPlot)
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
        self.styleLF = ttk.LabelFrame(self.editPane, text="Plot Style",
                                      relief=tk.RIDGE)
        self.styleLF.grid(row=thisrow, column=1, sticky=tk.W, pady=3)

        # - - - - - - - - - -
        # Row 5.0 - Plot/Scatter
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
        self.scatterStyle = tk.StringVar(self.styleLF, 'o')

        scatterStyle_kwargs = {'textvariable': self.scatterStyle,
                               'values': self.scatterStyleOptions,
                               'state': 'disabled',
                               'width': 4}

        self.scatterStyleCB = ttk.Combobox(self.styleLF,
                                           **scatterStyle_kwargs)

        self.lineOn.grid(row=0, column=0, padx=(0, 0))
        self.lineStyleCB.grid(row=0, column=1)
        self.lineStyleCB.bind('<<ComboboxSelected>>', self.startPlot)
        self.scatterOn.grid(row=0, column=2, padx=(10, 0))
        self.scatterStyleCB.grid(row=0, column=3)
        self.scatterStyleCB.bind('<<ComboboxSelected>>', self.startPlot)

        # - - - - - - - - - -
        # Row 5.1 - Legend
        self.showLegend = tk.BooleanVar(value=True)
        self.legendLoc = tk.StringVar(self.styleLF, value='Best')

        legendCB_kwargs = {'text': 'Show Legend', 'variable': self.showLegend,
                           'command': self.setLegendOptions, }
        self.legendCB = tk.Checkbutton(self.styleLF, **legendCB_kwargs)
        self.legendCB.grid(row=1, column=0, columnspan=2, sticky=tk.W)

        self.legendLocations = ('Best', 'Outside Right')
        legendLoc_kwargs = {'textvariable': self.legendLoc,
                            'values': self.legendLocations,
                            'state': 'readonly',
                            'width': 14}
        self.legendLocCB = ttk.Combobox(self.styleLF, **legendLoc_kwargs)
        self.legendLocCB.grid(row=1, column=2, columnspan=2, sticky=tk.E)
        self.legendLocCB.bind('<<ComboboxSelected>>', self.startPlot)

        # - - - - - - - - - -
        # Row 5.2 - Plot Color

        # Setting up whether the colors should be made automatically
        self.autoColor = tk.BooleanVar(value=True)
        ac_kwargs = {'text': 'Auto Color', 'variable': self.autoColor,
                     'command': self.showHidePlotColors, }
        self.autoColorCB = tk.Checkbutton(self.styleLF, **ac_kwargs)
        self.autoColorCB.grid(row=2, column=0, columnspan=2, sticky=tk.W)

        # Plot Color Picker
        pc_kwargs = {'width': 10, 'textvariable': self.plotColorHex,
                     'state': 'disabled', }
        self.plotColorEntry = ttk.Entry(self.styleLF, **pc_kwargs)

        # Adds a waiting period for the user to stop typing
        self.plotColorEntry.bind('<Key>', self.waitToPlot)
        self.plotColorEntry.grid(row=2, column=2, sticky=tk.E, pady=0)

        # Setting up color wheel buttong
        self.plotColorWheel = tk.PhotoImage(file='images/color_wheel.png')
        pcb_kwargs = {'image': self.plotColorWheel, 'state': 'disabled',
                      'command': self.pickPlotColor, }
        self.plotColorButton = tk.Button(self.styleLF, **pcb_kwargs)
        self.plotColorButton.grid(row=2, column=3, sticky=tk.W, padx=(5, 0))

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
                       'command': lambda: self.startPlot(1), }
        gmin_kwargs = {'text': 'Minor', 'variable': self.gridMinor,
                       'command': lambda: self.startPlot(1),
                       'state': 'disabled', }

        self.gridMajorCB = tk.Checkbutton(self.addOptsLF, **gmaj_kwargs)
        self.gridMajorCB.grid(row=0, column=1, sticky=tk.W,)

        self.gridMinorCB = tk.Checkbutton(self.addOptsLF, **gmin_kwargs)
        self.gridMinorCB.grid(row=0, column=2, sticky=tk.W,)

        # - - - - - - - - - -
        # Row 6.1 - Axis Labels
        self.showAxLabel = ttk.Label(self.addOptsLF, text='Axis Labels:',)
        self.showAxLabel.grid(row=1, column=0, sticky=tk.W, padx=(0, 2))
        self.showAxFrame = tk.Frame(self.addOptsLF)
        self.showAxFrame.grid(row=1, column=1, sticky=tk.W, columnspan=2)

        # ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
        # Row 6.1.0 - XYZ Labels
        self.showXLabel = tk.BooleanVar(value=True)
        self.showYLabel = tk.BooleanVar(value=True)
        self.showZLabel = tk.BooleanVar(value=True)
        xlbl_kwargs = {'text': 'X', 'variable': self.showXLabel,
                       'command': lambda: self.startPlot(1), }
        ylbl_kwargs = {'text': 'Y', 'variable': self.showYLabel,
                       'command': lambda: self.startPlot(1), }
        zlbl_kwargs = {'text': 'Z', 'variable': self.showZLabel,
                       'command': lambda: self.startPlot(1), }

        self.showXLabelCB = tk.Checkbutton(self.showAxFrame, **xlbl_kwargs)
        self.showXLabelCB.grid(row=0, column=0, sticky=tk.W)
        self.showYLabelCB = tk.Checkbutton(self.showAxFrame, **ylbl_kwargs)
        self.showYLabelCB.grid(row=0, column=1, sticky=tk.W)
        self.showZLabelCB = tk.Checkbutton(self.showAxFrame, **zlbl_kwargs)
        self.showZLabelCB.grid(row=0, column=2, sticky=tk.W)

        # - - - - - - - - - - - - - - - -
        # Row 7 - Run Traversal
        thisrow += 1
        self.runChoiceLF = ttk.LabelFrame(self.editPane, relief=tk.RIDGE,
                                          text="Run Viewer",)
        self.runChoiceLF.grid(row=thisrow, column=1, sticky=tk.W, pady=3,)

        # The switch for whether runs are plotted all together
        self.showAllRuns = tk.BooleanVar(value=True)

        # - - - - - - - - - -
        # Row 7.0 - Show All Runs
        allruns_kwargs = {'text': 'All', 'var': self.showAllRuns,
                          'value': True, 'command': lambda: self.startPlot(1)}

        self.allRunsRB = ttk.Radiobutton(self.runChoiceLF, **allruns_kwargs,)
        self.allRunsRB.grid(row=0, column=0, columnspan=1, sticky=tk.W)

        # - - - - - - - - - -
        # Row 7.1 - Show Some Runs
        someruns_kwargs = {'text': 'Select', 'var': self.showAllRuns,
                           'value': False,
                           'command': lambda: self.startPlot(1)}
        self.someRunsRB = ttk.Radiobutton(self.runChoiceLF, **someruns_kwargs,)
        self.someRunsRB.grid(row=0, column=1, columnspan=1, sticky=tk.W)

        # Setting up the chooser for the individual run
        self.run = tk.IntVar()
        run_kwargs = {'values': self.availableRuns.tolist(), 'width': 4,
                      'command': lambda: self.startPlot(1),
                      'state': 'disabled', 'textvariable': self.run, }
        self.runChoice = ttk.Spinbox(self.runChoiceLF, **run_kwargs)
        self.runChoice.grid(row=0, column=2, sticky=tk.W)
        self.runChoice.bind('<Key>', self.waitToPlot)

        # If there is an available run, set it to the first one
        if self.availableRuns.size > 0:
            self.runChoice.set(self.availableRuns[0])

        # Setting up transparency
        self.transparentRuns = tk.BooleanVar(value=True)
        transRun_kwargs = {'text': 'Fade Others', 'state': 'disabled',
                           'variable': self.transparentRuns,
                           'command': lambda: self.startPlot(1), }

        self.transRunsCB = tk.Checkbutton(self.runChoiceLF, **transRun_kwargs)
        self.transRunsCB.grid(row=0, column=3, sticky=tk.W,)

        self.setRunOptions()

    ####################################################################
    # Callback functions
    ####################################################################
    def modifyLimitsEntry(self, event: tk.Event, entry: str = None) -> None:
        """
        Modifies the Min/Max options for each variable (X/Y/Z) when the
        user clicks into or out of the field.

        If the field has Min (or Max) already in there, remove the
        text when the user enters the field.

        If the field has a non-float entry when the user leaves the field,
        restore Min (or Max) back to the field.

        Parameters
        ----------
        event : tk.Event
            Usually a focusIn or focusOut event which details whether
            the user has entered or left the field of interest
        entry : str, optional
            A metadescriptor which describes the location of where
            the user is or came from. The default is None.

        Returns
        -------
        None

        """
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

    def editTitleOptions(self, style: str = '') -> None:
        """
        Updates UI on whether user has pressed/unpressed the Bold Or Iatlic
        button and then has the plot title reflect that change.

        Parameters
        ----------
        style : str, optional
            A modifier parameter to indicate whether the bold or italic
            button has been pressed. The default is '' (for neither).

        Returns
        -------
        None

        """
        # Reading events
        if style == 'b':        # Swapping bold press state
            self.boldTitleOn = not self.boldTitleOn
        elif style == 'i':      # Swapping italic press state
            self.itTitleOn = not self.itTitleOn
        else:
            return              # Nothing to do

        # Swapping button behavior (pressed down or not)
        br = tk.SUNKEN if self.boldTitleOn else tk.FLAT
        ir = tk.SUNKEN if self.itTitleOn else tk.FLAT
        self.boldTitleButton.config(relief=br)
        self.itTitleButton.config(relief=ir)

        # Updating plot with new title style
        self.startPlot(1)

    def pickTitleColor(self) -> None:
        """
        Takes the color chosen by the user from the colorwheel button
        and renders the title with that color.

        Returns
        -------
        None

        """
        # Takes color from user (None if exited without choosing color)
        # Returns a tuple of ((R, G, B), Hex)
        # R, G, B are floating point!
        color = tkColorChooser.askcolor(color=self.titleColorRGB)
        if None not in color:
            # Sets the Hex value and updates the RGB value
            # The RGB value is used as the default in the colorchooser,
            # so that is why it needs to get set
            self.titleColorHex.set(color[1])
            self.titleColorRGB = self.hex2rgb(self.titleColorHex.get())
            self.editTitleOptions(self.titleColorHex.get())
        self.startPlot(1)

    def pickPlotColor(self) -> None:
        """
        Takes the color chosen by the user from the colorwheel button
        and renders the plot with that color.

        Returns
        -------
        None

        """
        # Takes color from user (None if exited without choosing color)
        # Returns a tuple of ((R, G, B), Hex)
        # R, G, B are floating point!
        color = tkColorChooser.askcolor(color=self.plotColorRGB)
        if None not in color:
            # Sets the Hex value and updates the RGB value
            # The RGB value is used as the default in the colorchooser,
            # so that is why it needs to get set
            self.plotColorHex.set(color[1])
            self.plotColorRGB = self.hex2rgb(self.plotColorHex.get())
            self.startPlot(1)

    def setLegendOptions(self) -> None:
        """
        Enables or disables the combobox for legend locations based
        on whether the box is checked

        Returns
        -------
        None
            DESCRIPTION.

        """
        if self.showLegend.get():
            self.legendLocCB['state'] = 'readonly'
        else:
            self.legendLocCB['state'] = 'disabled'

        self.startPlot(1)

    def setDimensions(self) -> None:
        """
        Sets the dimensions for the plot based upon the columns
        selected by the user. If the user does not select both the
        x and y axis columns, then the dimensions are set to 0.
        If the user selects both x and y but not z, the dimension is 2.
        If the user selects x, y, and z, the dimension is 3

        Returns
        -------
        None

        """
        if self.xCol.get() == '':       # x does not exist
            self.dimensions = 0
            return
        elif self.yCol.get() == '':     # x exists, y does not
            self.dimensions = 0
            return
        elif self.zCol.get() == '':     # x and y exist, z does not
            self.dimensions = 2

            # Minor grid option exists on 2D graphs
            self.gridMinorCB['state'] = 'normal'
        else:
            self.dimensions = 3         # x, y, and z exist

            # 3D plots include a major grid by default
            # Minor grids in 3D introduce a bug
            self.gridMinorCB['state'] = 'disabled'
            self.gridMajorCB['state'] = 'disabled'

        # If any two columns match, there is no need to plot
        if (self.xCol.get() == self.yCol.get()
           or self.xCol.get() == self.zCol.get()
           or self.yCol.get() == self.zCol.get()):
            self.dimensions = 0
            self.status.set('Plot will not render if two elements match')

    def setRunOptions(self, event=None) -> None:
        """
        Sets the run numbers specified for looking at runs.
        Can enable/disable run number input based upon user selection.
        Will also set default values for the run number if there is
        an available set of run numbers to choose from

        Parameters
        ----------
        event : tk.Event, optional
            An event to be passed to turn this function into a handle.
            Not currently needed.
            The default is None.

        Returns
        -------
        None

        """

        # Set the ability for the user to edit the value based on choice
        newstate = 'disabled' if self.showAllRuns.get() else 'normal'
        self.runChoice['state'] = newstate
        self.transRunsCB['state'] = newstate

        # Load the spinbox with the available choices if they exist
        if self.availableRuns.size > 0:
            self.runChoice['values'] = self.availableRuns.tolist()

            # If there is no value in the box, set it
            if self.runChoice.get() == '0':
                self.runChoice.set(self.availableRuns[0])
        else:
            self.runChoice.set('')
            return

        # We need to do some value checking but will not be able to
        # if there are no values to choose from
        try:
            # if there is no entry for self.run to select from, it
            # will be assigned an empty string and then try to do
            # type conversion. This will obviously fail.
            run = self.run.get()
        except tk.TclError as tkTcl:
            assert(tkTcl)  # to shut linter up
            return

        # If the value typed in does not match any value in the
        # list of available runs, match it to the nearest value
        if isinstance(run, int) and run not in self.availableRuns:
            diff_vals = np.abs(self.availableRuns - run)
            nearest_idx = np.argmin(diff_vals)
            newval = self.availableRuns[nearest_idx]
            self.runChoice.set(newval)

    def setVals(self) -> None:
        """
        Checks whether user has selected X, Y, or Z columns from the
        ComboBox (drop-down) and sets the x, y, and z vectors from
        those choices.

        If both X and Y are not selected, nothing happens.
        If X and Y are selected but not Z, then a 2D plot will be rendered.
        If X, Y, and Z are selected, a 3D plot will be rendered.

        Returns
        -------
        None

        """

        # Guarantees dimensions are up to date
        self.setDimensions()

        # If no dimensions, set values to nothing
        if self.dimensions == 0:
            self.x, self.y, self.z = [], [], []

        # If only 2D plot, only set x and y
        elif self.dimensions == 2:
            self.x = self.missileDF[self.xCol.get()].values
            self.y = self.missileDF[self.yCol.get()].values

        # If 3D plot, set x, y, and z
        elif self.dimensions == 3:
            self.x = self.missileDF[self.xCol.get()].values
            self.y = self.missileDF[self.yCol.get()].values
            self.z = self.missileDF[self.zCol.get()].values
        return

    def getTopDir(self) -> None:
        """
        Opens a file browswer for the run files. Once selected,
        the chosen file path will show in the text field.
        The path can be typed in also.
        ** Only a directory can be selected

        Returns
        -------
        None

        """

        kwargs = {'title': 'Select Directory Containing Run(s)',
                  'mustexist': True, }

        # If you have not selected a path, set up a default path
        # If something is already set, the file dialog should default there
        if self.topDir == '':
            kwargs['initialdir'] = self.default_path()
        else:
            kwargs['initialdir'] = self.topDir

        selection = filedialog.askdirectory(**kwargs)
        if selection != '':
            self.topDir = os.path.abspath(selection)

        # Updates text widget with path (deletes old path)
        self.topDirPath.delete('1.0', tk.END)
        self.topDirPath.insert(1.0, self.topDir)

    def loadFromTopDir(self) -> None:
        """
        Loads missile file from topDir, if possible.
        If directory is invalid, display a warning message.
        If missile file loads successfully, update status.

        Returns
        -------
        None

        """
        # If the entry is not a valid directory, display a warning message
        if not os.path.isdir(self.topDir):
            self.status.set('No file(s) loaded')
            mb.showinfo('Invalid directory',                 # title
                        'Please choose a valid directory!',  # message
                        icon='warning',)
            return

        # This should already be true, but setting just in case
        self.topDir = os.path.abspath(self.topDir)
        self.loadMissileFiles()

    def loadMissileFiles(self) -> str:
        """
        Checks for whether 'NotionalETEOutput###.xlsx' is present in topDir.
        (The ### is a random number between 000 and 999, always three digits)
        If present, loads the missile file into a dataframe, updates the
        dataframe columns, and makes available for plotting only the
        dataframe columns that have floating-point data

        ** Will definitely need to be updated upon porting

        Returns
        -------
        str
            The absolute path to the missile file

        """
        self.status.set(f'Searching {self.topDir} for files')  # updating user

        # Looking for files to read in directory
        tree = dirTree(self.topDir)
        missileFiles = allMissileFiles(tree)

        # Making massive DataFrame of all the missile files in tree
        N = len(missileFiles)
        self.status.set(f'Loading {N} file' + 's' * (N > 1))
        self.missileDF = combinedMissleDF(missileFiles)
        self.missileDF.rename(columns=dictMap(), inplace=True)
        self.status.set(f'Loaded {N} file' + 's' * (N > 1))

        # Determining available runs based upon unique IDs
        if 'RunNumber' in self.missileDF.columns:
            self.availableRuns = self.missileDF.RunNumber.unique()
            self.setRunOptions()
            self.run.set(self.availableRuns[0])

        # Takes the columns from the DataFrame and makes them available
        # to be plotted on any axis. The first entry will be blank
        # so that users must choose to plot
        self.plotCols = [''] + sorted([col for col, val
                                       in self.missileDF.dtypes.items()
                                       if val == np.dtype('float64')])
        self.xCB['values'] = self.plotCols
        self.yCB['values'] = self.plotCols
        self.zCB['values'] = self.plotCols

    def getOutDir(self) -> None:
        """
        Opens a file browswer for the output files.
        Once selected, the chosen file path will show in the text field.
        (The path can be typed in also.)
        ** Only a directory (not a file) can be selected

        Returns
        -------
        None

        """

        kwargs = {'title': 'Select Ouput Directory',
                  'initialdir': self.default_path(), }
        self.outDir = filedialog.askdirectory(**kwargs)
        self.outDir = os.path.abspath(self.outDir)

        # Updates text widget with path (deletes old path)
        self.outDirPath.delete('1.0', tk.END)
        self.outDirPath.insert(1.0, self.outDir)

    def setStatusBarOptions(self, event=None) -> None:
        """
        Updates the the elements displayed in the status bar.

        Parameters
        ----------
        event : tk.Event, optional
            An event that can drive the call. The default is None.

        Returns
        -------
        None

        """

        # Capturing current tab
        tab = self.tabs.index(self.tabs.select())

        if tab == 0:  # Data Input Tab
            self.xkcdModeCB.pack_forget()
        elif tab == 1:  # Viewer Tab
            self.xkcdModeCB.pack(fill=tk.BOTH, side=tk.RIGHT)
        else:
            self.status.set(f'You are on tab {tab} which must be new')

    def setPlotStyleOptions(self) -> None:
        """
        Checks whether the radio button for 'line' or 'scatter' is selected.
        For the selected option, it makes the ComboBox (drop-down)
        active and selectable by the user

        Returns
        -------
        None

        """
        if self.plotStyle.get() == 'line':
            self.lineStyleCB.config(state='readonly')
            self.scatterStyleCB.config(state='disabled')
        if self.plotStyle.get() == 'scatter':
            self.lineStyleCB.config(state='disabled')
            self.scatterStyleCB.config(state='readonly')
        self.startPlot('update')  # Need a non-None event

    def showHidePlotColors(self) -> None:
        """
        Changes the ability to interact with the plotColor entry and button
        elements based upon whether autoColor has been selected

        Returns
        -------
        None

        """

        # Disables the ability to edit if the autocolor option is set
        # Otherwise, restores it to normal
        newstate = 'disabled' if self.autoColor.get() else 'normal'
        self.plotColorEntry['state'] = newstate
        self.plotColorButton['state'] = newstate

        # Updates plot based on choice
        self.startPlot(1)

    def showHideXLimits(self) -> None:
        """
        Determines whether or not to display the boxes for setting
        the minimum and maximum limits for the X variable.
        Checks the status of the tk.CheckBox in the GUI to determine
        behavior

        Returns
        -------
        None

        """
        if self.xLimits.get():  # if checked, show entry fields
            self.xMinEntry.grid(row=self.xLimitsRow, column=2)
            self.xMaxEntry.grid(row=self.xLimitsRow, column=3)
        else:                   # hide fields
            self.xMinEntry.grid_remove()
            self.xMaxEntry.grid_remove()
        self.startPlot(1)

    def showHideYLimits(self) -> None:
        """
        Determines whether or not to display the boxes for setting
        the minimum and maximum limits for the Y variable.
        Checks the status of the tk.CheckBox in the GUI to determine
        behavior

        Returns
        -------
        None

        """
        if self.yLimits.get():  # if checked, show entry fields
            self.yMinEntry.grid(row=self.yLimitsRow, column=2)
            self.yMaxEntry.grid(row=self.yLimitsRow, column=3)
        else:                   # hide fields
            self.yMinEntry.grid_remove()
            self.yMaxEntry.grid_remove()
        self.startPlot(1)

    def showHideZLimits(self) -> None:
        """
        Determines whether or not to display the boxes for setting
        the minimum and maximum limits for the Z variable.
        Checks the status of the tk.CheckBox in the GUI to determine
        behavior

        Returns
        -------
        None

        """
        if self.zLimits.get():  # if checked, show entry fields
            self.zMinEntry.grid(row=self.zLimitsRow, column=2)
            self.zMaxEntry.grid(row=self.zLimitsRow, column=3)
        else:                   # hide fields
            self.zMinEntry.grid_remove()
            self.zMaxEntry.grid_remove()
        self.startPlot(1)

    ####################################################################
    # Utility functions
    ####################################################################
    def default_path(self) -> str:
        """
        Gives an OS-specific default path to display in filedialog
        windows

        Returns
        -------
        str
            'C:' for Windows, '/' for Unix, '//' for Linux
            Not currently defined for other operating systems

        """
        defaultPaths = {'windows': 'C:\\',
                        'unix': '/',
                        'linux': '//',
                        'macos': None,
                        'sunos': None,
                        }
        thisOS = platform.system().lower()
        return defaultPaths[thisOS]

    def waitToPlot(self, event=None) -> None:
        """
        Creates a queue to wait for an event to finish. This allows users
        to enter multiple keystrokes or perform other actions before the
        GUI automatically updates.

        A particular usage is in letting users enter a title without the
        GUI trying to update the graph after after each letter.

        Parameters
        ----------
        event : tkinter.Event, optional
            The event being potentially held. The default is None.

        Returns
        -------
        None

        """

        # cancel the old job
        if self._after_id is not None:
            self.after_cancel(self._after_id)

        # create a new job
        self._after_id = self.after(1500, lambda: self.startPlot(event=event))

    def autosizer(self, event=None) -> None:
        """
        Adjusts the tkinter Notebook (tabbed) section size automatically.

        Parameters
        ----------
        event : tkinter.Event, optional
            A parameter to catch any trace passes. The default is None.

        Returns
        -------
        None

        """
        self.tabs.config(height=self.winfo_height()-50,
                         width=self.winfo_width()-145)

    def hex2rgb(self, hexstring: str) -> tuple:
        """
        A method to convert 6-digit hexadecimal values to a triplet
        of values in the range (0-255)

        Parameters
        ----------
        hexstring : str
            A hex color string in the form #XXXXXX, where each X is
            a hexadecimal number

        Returns
        -------
        tuple
            A triplet of the form (A, B, C) where A, B, and C are integers
            between 0 and 255 (inclusive)

        """
        rgb = []
        for i in range(3):
            # The first element of the string is '#'
            # Each section of two digits is sliced off
            string_ = hexstring[1 + 2 * i:1 + 2 * (i + 1)]

            # Converts the hex value to an integer in [0, 255]
            rgb.append(int(f'0x0000{string_}', 0))
        return tuple(rgb)

    ####################################################################
    # Plotting functions
    ####################################################################

    def plotDF(self) -> pd.DataFrame:
        """
        Generates a smaller dataframe for plotting from the massive
        one stored in memory

        Returns
        -------
        plotDF : pd.DataFrame
            A 2 or 3 column Pandas DataFrame containing the x, y, and
            sometimes z data for plotting

        """
        # Setting up a renaming convention to make plotting easier
        xyzRenamer = {self.xCol.get(): 'x', self.yCol.get(): 'y',
                      self.zCol.get(): 'z'}

        # Determining which columns to keep
        plotCols = [self.xCol.get(), self.yCol.get()]
        if self.dimensions == 3:
            plotCols.append(self.zCol.get())

        # Downselecting DataFrame based on these columns
        # Keeping Unique ID so we can plot each ID separately
        plotDF = self.missileDF[['RunNumber', *plotCols]].copy()

        # If we don't want to show all the runs and don't
        # want them to be transparent, we can downselect the values now
        if not self.showAllRuns.get() and not self.transparentRuns.get():
            plotDF = plotDF.query(f'RunNumber=={self.run.get()}').copy()

        # This will allow us to reference plotDF.x
        # instead of having to call plotDF[self.xCol.get()], for example
        return plotDF.rename(columns=xyzRenamer, inplace=False)

    def startPlot(self, event=None, item=None, mode=None) -> None:
        """
        Sets up all the variables and options necessary to generate
        a plot in the viewer pane.

        Parameters
        ----------
        event : int or tkinter.Event, optional
            Often called as a 1 instead of tk.Event.
            If not None, indicates that the plot should update
            The default is None.
        item : tkinter.Event, optional
            Only passed when using a trace.
            (tkinter Events are passed as triples.)
            The default is None.
        mode : tkinter.Event, optional
            Only passed when using a trace.
            (tkinter Events are passed as triples.)
            The default is None.

        Returns
        -------
        None

        """

        # If there's no reason to update, don't update
        if event is None:
            print(event, item, mode)    # This is mostly for debugging
            return

        # Close old figure and toolbar if they already exist
        if None not in (self.figure, self.canvas, self.toolbar):
            plt.close(self.figure)
            self.canvas.get_tk_widget().pack_forget()
            self.toolbar.pack_forget()

        # Loading data for plotting
        self.setVals()

        # Setting the run numbers to consider
        self.setRunOptions()

        # If there is nothing to plot, leave canvas blank
        if self.dimensions == 0:
            return

        # Settng up canvas to draw plot
        if self.xkcdMode.get():             # Easter Egg Mode
            with plt.xkcd():
                self.figure = plt.Figure()
                self.finishPlot()
        else:
            self.figure = plt.Figure()
            self.finishPlot()

    def finishPlot(self) -> None:
        """
        Generates a new plot on the figure set up in startPlot.

        Returns
        -------
        None

        """

        self.canvas = FigureCanvasTkAgg(self.figure, self.viewPane)
        self.canvas.draw()

        # Setting up subplot for showing all the plots
        subplot_kwargs = {'projection': '3d' if self.dimensions == 3 else None}
        myplot = self.figure.add_subplot(111, **subplot_kwargs)

        # This may need to be edited for multiple graph support
        plot_kwargs = {}

        # If autocoloring is turned off, set the color for the graph
        if not self.autoColor.get():
            plot_kwargs = {'color': self.plotColorEntry.get(), }

        # Looping through all possible unique IDs and adding plots
        for (uid, df) in self.plotDF().groupby(['RunNumber']):
            plot_kwargs['label'] = f'{uid}'

            # If the transparency setting is on, we want to highlight
            # only the run of interest
            if (
              not self.showAllRuns.get()
              and self.transparentRuns.get()
              and uid != self.run.get()):
                plot_kwargs['alpha'] = 0.2
            else:
                plot_kwargs['alpha'] = 1.0

            # This segments the data into 2 or 3 dimensions, depending
            # on whether we are plotting 2D or 3D data
            plotlist = [df.x.values, df.y.values]
            if self.dimensions == 3:
                plotlist.append(df.z.values)

            # Plotting line or scatter based on user input
            if self.plotStyle.get() == 'line':
                myplot.plot(*plotlist, **plot_kwargs,
                            linestyle=self.lineStyle.get())
            else:
                myplot.scatter(*plotlist, **plot_kwargs,
                               marker=self.scatterStyle.get())

        # Show legend if selected
        if self.showLegend.get():
            legend_kwargs = {'title': 'Run Number',
                             'fancybox': True, 'shadow': True, }

            # Setting the location for the legend based on user input
            if self.legendLoc.get() == 'Best':
                pass
            elif self.legendLoc.get() == 'Outside Right':
                legend_kwargs['bbox_to_anchor'] = (1.1, 1.0)

            myplot.legend(**legend_kwargs)

        # Adding Axes Labels
        if self.showXLabel.get():
            myplot.set_xlabel(self.xCol.get())
        if self.showYLabel.get():
            myplot.set_ylabel(self.yCol.get())
        if self.dimensions == 3 and self.showZLabel.get():
            myplot.set_zlabel(self.zCol.get())

        # Adding gridlines, if necessary
        if self.gridMajor.get():
            myplot.grid(b=True, which='major', alpha=0.8)
        if self.gridMinor.get():
            myplot.grid(b=True, which='minor', alpha=0.2, linestyle='--',)
        else:
            self.status.set('')

        # Setting the min/max values for each variable
        (xMin, xMax, yMin, yMax, zMin, zMax) = self.getLimits(myplot)
        myplot.set_xlim(xMin, xMax)
        myplot.set_ylim(yMin, yMax)
        if self.dimensions == 3:
            myplot.set_zlim(zMin, zMax)

        # Adding title with options, if necessary
        if self.titleText.get() != '':
            plotTitle = self.titleText.get()
            fontdict = {'fontsize': int(self.titleSize.get()),
                        'color': self.titleColorHex.get(),
                        'style': 'italic' if self.itTitleOn else 'normal',
                        'fontweight': 'bold' if self.boldTitleOn else 'normal'}
            myplot.set_title(plotTitle, fontdict=fontdict)

        # Packing plot into GUI and adding toolbar
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM,
                                         fill=tk.BOTH,
                                         expand=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.viewPane)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def getLimits(self, ax) -> tuple:
        """
        Returns the limits to be used in a plot based upon the default
        limits given by pyplot and the limits (potentially) specified
        by the user in the GUI

        Parameters
        ----------
        ax : matplotlib.axes._subplots.AxesSubplot
            A handle to the subplot which will have new limits
            This cannot be type hinted because the type is created
            on the fly

        Returns
        -------
        tuple
            A six-element tuple of the minimum and maximum values for
            x, y, and z, respectively

        """
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
        else:
            # This guarantees a six-element return tuple each time
            zMin, zMax = (0, 0)

        xyzLimits = (xMin, xMax, yMin, yMax, zMin, zMax)
        return xyzLimits


####################################################################
# Mapper for DataFrame Columns
####################################################################

def dictMap():
    """
    A mapper to take columns from the input file and generate
    meaningful, human-readable columns. Intended to be used
    with the .rename() function for a dataframe.

    Returns
    -------
    dMap : dict
        A mapping str->str intended to be used for dataframes

    """
    dMap = {
        'uniqueid': 'RunNumber',
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


####################################################################
# Directory parsing functions
####################################################################

def dirTree(root: str) -> list:
    """
    Generates a list containing a directory and all its subdirectories.

    Parameters
    ----------
    root : str
        A top-level directory to traverse.

    Returns
    -------
    list
        The directory and all subdirectories.

    """
    # Scan directory and keep only subdirectories
    subdirs = [x.path for x in os.scandir(root) if x.is_dir()]

    # Recursively call dirtree() on the subdirectories
    subtree = [dirTree(x) for x in subdirs]

    # Building a list of all the items in the subdirectories
    tree = [root]
    for list_ in subtree:    # Each element in the subtree is a list
        for dir_ in list_:
            tree.append(dir_)
    return tree


def allMissileFiles(
        dirlist: list,
        mfile_regex: str = 'NotionalETEOutput(\\d+).xlsx') -> list:
    """
    Generates a list of files from the supplied directory list
    which match the specified pattern.

    Parameters
    ----------
    dirlist : list
        A list of directories to check for files
    mfile_regex : str, optional
        The matching criterion (regular expression).
        The default is 'NotionalETEOutput(\\d+).xlsx'.

    Returns
    -------
    list
        The path for each file matching the criterion.

    """

    missileFiles = []
    for dir_ in dirlist:
        for item in os.scandir(dir_):
            if item.is_file():
                check = re.match(mfile_regex, item.name)
                if check is not None:
                    missileFiles.append(item.path)
    return missileFiles


def combinedMissleDF(missileFileList: list) -> pd.DataFrame:
    """
    Combines a list of input files into a single DataFrame by
    generating a single DataFrame for each file and using the
    concatenation function to generate a single object.

    Transforms Path and uniqueID into categorical variables because
    it's going to have a lot of repeats

    Parameters
    ----------
    missileFileList : list
        The path to each file to be combined into the DataFrame

    Returns
    -------
    pd.DataFrame
        A Pandas DataFrame of the combined object

    """
    df = pd.concat(map(makeDataFrameAddPath, missileFileList))
    # df.Path = df.Path.astype('category')
    # df.uniqueid = df.uniqueid.astype('category')
    return df


def makeDataFrameAddPath(inFile: str) -> pd.DataFrame:
    """
    Makes a DataFrame from an Excel file and adds the path
    of the file as a new column

    Parameters
    ----------
    inFile : str
        An Excel spreadsheet that has panel data

    Returns
    -------
    df : pd.DataFrame
        A Pandas DataFrame of the data with one additional column added

    """
    df = pd.read_excel(inFile)
    df['Path'] = inFile
    return df


# To prevent this running automatically if imported
if __name__ == "__main__":
    app = SimpleGUI()
    try:
        assert Axes3D  # to silence the linter
        app.mainloop()
    except KeyboardInterrupt:
        app.destroy()
        print('Terminated')
