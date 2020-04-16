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

# TODO: Split up graph styles across two lines
# TODO: Add a series of fields for each separate graph
# TODO: Add option for legend
# TODO: Add option for x/y/z labels (use labelframe)
# TODO: Add callback function for xyzLimits to update value meaningfully
#       -> Try using try/except to see if the value makes sense as a number
# TODO: Add LF and put X/Y/Z dropdowns inside of it
# TODO: Add button to render graph manually
# TODO: Add color picker for graph options
# TODO: Add manual color entry
# TODO: Add font options:
#       -> Family
#       -> Underline


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

        # TODO: Change "state" to 'readonly' and implement extensions
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
        self.xyzMinMaxFrame.grid(row=thisrow, column=1, sticky=tk.W,)
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

        # Entry for maximum Y value
        self.xMax = tk.StringVar()
        self.xMaxEntry = tk.Entry(self.xyzMinMaxFrame, **limitskwargs)
        self.xMaxEntry['textvariable'] = self.xMax
        self.xMaxEntry.insert(0, 'Max')

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

        # Entry for maximum Y value
        self.yMax = tk.StringVar()
        self.yMaxEntry = tk.Entry(self.xyzMinMaxFrame, **limitskwargs)
        self.yMaxEntry['textvariable'] = self.yMax
        self.yMaxEntry.insert(0, 'Max')

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

        # Entry for maximum Z value
        self.zMax = tk.StringVar()
        self.zMaxEntry = tk.Entry(self.xyzMinMaxFrame, **limitskwargs)
        self.zMaxEntry['textvariable'] = self.zMax
        self.zMaxEntry.insert(0, 'Max')

        # - - - - - - - - - - - - - - - -
        # Row 4 - Custom Title
        thisrow += 1
        self.titleLF = ttk.LabelFrame(self.editPane, text="Custom Title",
                                      relief=tk.RIDGE)
        self.titleLF.grid(row=thisrow, column=1, sticky=tk.W,)

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
        self.boldTitleButton = tk.Button(self.titleLF, text="B", width=3,
                                         relief=tk.FLAT,
                                         font=boldFont,
                                         command=lambda: self.editTitle('b'),)
        self.boldTitleButton.grid(row=1, column=1,)

        # Italic button
        itFont = font.Font(size=10, slant="italic")
        self.itTitleButton = tk.Button(self.titleLF, text="I", width=3,
                                       relief=tk.FLAT,
                                       font=itFont,
                                       command=lambda: self.editTitle('i'),)
        self.itTitleButton.grid(row=1, column=2,)

        # Color Picker
        tc_kwargs = {'width': 8, 'textvariable': self.titleColorHex, }
        self.titleColorEntry = ttk.Entry(self.titleLF, **tc_kwargs)

        # Adds a waiting period for the user to stop typing
        self.titleColorEntry.bind('<Key>', self.handle_wait)
        self.titleColorEntry.grid(row=1, column=3, sticky=tk.W)

        # Setting up color wheel buttong
        self.colorWheel = tk.PhotoImage(file='images/color_wheel.png')
        self.titleColorButton = tk.Button(self.titleLF, image=self.colorWheel,
                                          command=self.pickColor)
        self.titleColorButton.grid(row=1, column=4,)

        # - - - - - - - - - - - - - - - -
        # Row 5 - Style Options
        thisrow += 1

        self.styleLF = ttk.LabelFrame(self.editPane, text="Plot Style Options",
                                      relief=tk.RIDGE)
        self.styleLF.grid(row=thisrow, column=1, sticky=tk.W,)

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

    ####################################################################
    # Callback functions
    ####################################################################
    def todo(self):
        pass

    def editTitle(self, event=None):
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

    def pickColor(self):
        color = tkColorChooser.askcolor(color=self.titleColorRGB)
        if None not in color:
            self.titleColorHex.set(color[1])
            self.titleColorRGB = self.hex2rgb(self.titleColorHex.get())
            self.editTitle(self.titleColorHex.get())

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

    def showHideYLimits(self):
        if self.yLimits.get():  # if checked
            self.yMinEntry.grid(row=self.yLimitsRow, column=2)
            self.yMaxEntry.grid(row=self.yLimitsRow, column=3)
        else:
            self.yMinEntry.grid_remove()
            self.yMaxEntry.grid_remove()

    def showHideZLimits(self):
        if self.zLimits.get():  # if checked
            self.zMinEntry.grid(row=self.zLimitsRow, column=2)
            self.zMaxEntry.grid(row=self.zLimitsRow, column=3)
        else:
            self.zMinEntry.grid_remove()
            self.zMaxEntry.grid_remove()

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
        # myplot.plot(*plotlist, color="#C41E3A", marker="o", linestyle="")

        if self.plotStyle.get() == 'line':
            myplot.plot(*plotlist, linestyle=self.lineStyle.get())
        else:
            myplot.scatter(*plotlist, marker=self.scatterStyle.get())

        if self.titleText.get() != '':
            label = self.titleText.get()
            fontdict = {'fontsize': int(self.titleSize.get()),
                        'color': self.titleColorHex.get(),
                        'style': 'italic' if self.itTitleOn else 'normal',
                        'fontweight': 'bold' if self.boldTitleOn else 'normal'}
            myplot.set_title(label, fontdict=fontdict)

        self.canvas = FigureCanvasTkAgg(self.figure, self.viewPane)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM,
                                         fill=tk.BOTH,
                                         expand=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.viewPane)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


app = SimpleGUI()
try:
    assert Axes3D  # to silence the linter
    app.mainloop()
except KeyboardInterrupt:
    app.destroy()
    print('Terminated')
