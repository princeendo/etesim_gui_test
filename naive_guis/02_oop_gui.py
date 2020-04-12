# -*- coding: utf-8 -*-

# Module-Level Imports
import os
import platform
import numpy as np
import tkinter as tk
from tkinter import messagebox as mb
from tkinter import ttk
from tkinter import filedialog
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# The original function was deprecated so we're importing the new one
# to match the tutorial more closely
from matplotlib.backends.backend_tkagg import (NavigationToolbar2Tk
                                               as NavigationToolbar2TkAgg)
from matplotlib.figure import Figure

# Imports and settings for Tkinter
import matplotlib
matplotlib.use("TkAgg")  # To use with Tkinter


# LARGE_FONT = ("Verdana", 12)

# TODO: Add Color Option for Graphs
# TODO: Split up graph styles across two lines
# TODO: Add a series of fields for each separate graph
# TODO: Add plot title
# TODO: Add option for legend
# TODO: Add labels and ComboBoxes for each parameter
# TODO: Add callback function for xyzLimits to update value meaningfully
#       -> Try using try/except to see if the value makes sense as a number


class SimpleGUI(tk.Tk):
    def __init__(self, *args, **kwargs):

        # initializing and adding a GUI icon and title
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.iconbitmap(self, default="images/window_icon_radar.ico")
        tk.Tk.wm_title(self, "ETESim Plotting Suite")
        self.geometry("650x250+450+250")

        self.plotCols = ['']

        # Creating a Notebook seems to be the key to making tabs
        self.tabs = ttk.Notebook(self,)

        # The fill can go horizontal (tk.X), vertical (tk.Y), or all (tk.BOTH)
        # I assume the "expand" keyword allows for it to fill the space
        self.tabs.pack(fill=tk.BOTH, expand=True)

        self.build_tabs()

    def build_tabs(self):
        ################################################################
        # Tab 1: Data Input
        ################################################################
        self.tab1 = ttk.Frame(self.tabs,)
        self.datainput_icon = tk.PhotoImage(file='images/input-data-1.png')
        self.tabs.add(self.tab1,
                      text='Data Input',
                      image=self.datainput_icon,
                      compound=tk.LEFT,)

        ########################################
        # Row 0 - Browsing for Directory
        ########################################
        self.topDirLabel = tk.Label(self.tab1, text='Directory with Run(s): ')
        self.topDirLabel.grid(row=0, sticky=tk.W)

        self.topDir = ''
        self.topDirPath = tk.Text(self.tab1, relief=tk.SUNKEN)
        self.topDirPath.config(width=40, height=1.45)
        self.topDirPath.grid(row=0, column=1, columnspan=5, sticky=tk.W)

        self.topDirBrowseButton = tk.Button(self.tab1,
                                            text='Browse',
                                            height=1,
                                            command=self.getTopDir)
        self.topDirBrowseButton.grid(row=0, column=6, padx=4)

        self.topDirLoadButton = tk.Button(self.tab1,
                                          text='Load',
                                          height=1,
                                          command=self.loadFromTopDir)
        self.topDirLoadButton.grid(row=0, column=7, padx=4)

        ########################################
        # Row 1 - Threat Type(s)
        ########################################
        self.threatTypeOptions = ('Infer', 'ABT', 'TBM')
        self.threatTypeLabel = tk.Label(self.tab1, text='Threat: ')
        self.threatTypeLabel.grid(row=1, sticky=tk.W)
        self.threatType = tk.StringVar()
        self.threatTypeComboBox = ttk.Combobox(self.tab1,
                                               textvariable=self.threatType,
                                               values=self.threatTypeOptions,
                                               state='readonly',
                                               width=20,)

        self.threatTypeComboBox.set('Infer')  # Could use .current(0)
        self.threatTypeComboBox.grid(row=1, column=1, columnspan=2)

        ################################################################
        # Tab 2: Graph Options
        ################################################################
        gs_ico = 'images/graph-settings-icon.png'
        self.graphsettings_icon = tk.PhotoImage(file=gs_ico)
        self.tab2 = ttk.Frame(self.tabs,)
        self.tabs.add(
                self.tab2,
                text='Graph Options',
                image=self.graphsettings_icon,   # The icon feature is awesome
                compound=tk.LEFT,)               # Places icon left of text

        ########################################
        # Row 0 - Number of Plots
        ########################################
        thisrow = 0
        # Setting up a 'spinbox' where you can only select a range of values
        self.numPlots = tk.IntVar(self.tab2, 1)
        self.numPlotsLabel = ttk.Label(self.tab2, text='Simultaneous Plots: ')
        self.numPlotsLabel.grid(row=thisrow, column=0, padx=(0, 10))

        # This can be done with tk or ttk
        # If using tk, the default value is from_ or use the "value" keyword
        # If using ttk, you have to set the default value with .set()
        self.numPlotsSpinBox = ttk.Spinbox(self.tab2,
                                           from_=1,
                                           to=5,
                                           command=self.setNumPlots,
                                           width=3,
                                           state='readonly',)  # to limit input
        self.numPlotsSpinBox.insert(0, '1')
        self.numPlotsSpinBox.grid(row=thisrow, column=1)
        self.numPlotsSpinBox.set('1')

        ########################################
        # Row 1 - 2D/3D Options
        ########################################
        thisrow += 1
        self.dimensions = tk.IntVar(self.tab2, 2)
        self.dimensionsLabel = tk.Label(self.tab2, text='Dimensions: ')
        self.dimensionsLabel.grid(row=thisrow, column=0, sticky=tk.W,)
        self.radio2D = ttk.Radiobutton(self.tab2,
                                       text='2D',       # Button text
                                       value=2,         # Stored value
                                       var=self.dimensions,
                                       command=self.setGraphDimensions,)
        self.radio3D = ttk.Radiobutton(self.tab2,
                                       text='3D',       # Button text
                                       value=3,         # Stored value
                                       var=self.dimensions,
                                       command=self.setGraphDimensions,)

        self.radio2D.grid(row=thisrow, column=1,)
        self.radio3D.grid(row=thisrow, column=3,)

        ########################################
        # Row 2 - Plot Style Options
        ########################################
        thisrow += 1
        self.plotOptions = ('line', 'scatter')
        self.plotStyle = tk.StringVar(self.tab2, 'line')
        self.plotStyleLabel = tk.Label(self.tab2, text='Plot Style: ',)
        self.plotStyleLabel.grid(row=thisrow, column=0, sticky=tk.W)
        self.lineOn = ttk.Radiobutton(self.tab2,
                                      text='Line',          # Button text
                                      value='line',         # Stored value
                                      var=self.plotStyle,
                                      command=self.setPlotStyleOptions,)
        self.scatterOn = ttk.Radiobutton(self.tab2,
                                         text='Scatter',       # Button text
                                         value='scatter',      # Stored value
                                         var=self.plotStyle,
                                         command=self.setPlotStyleOptions,)

        # Setting up a ComboBox to be placed beside Line Style radio button
        self.lineStyleOptions = ('-', '--', ':', '-.', )
        self.lineStyle = tk.StringVar(self.tab2, '-')
        lineStyle_kwargs = {'textvariable': self.lineStyle,
                            'values': self.lineStyleOptions,
                            'state': 'readonly',
                            'width': 5}
        self.lineStyleComboBox = ttk.Combobox(self.tab2, **lineStyle_kwargs)

        # Setting up a ComboBox to be placed beside Scatter Style radio button
        self.scatterStyleOptions = ('o', 'v', '^', '<', '>', '8', 's', 'p',
                                    '*', 'h', 'H', 'D', 'd', 'P', 'X')
        self.scatterStyle = tk.StringVar(self.tab2, 'o')

        scatterStyle_kwargs = {'textvariable': self.scatterStyle,
                               'values': self.scatterStyleOptions,
                               'state': 'disabled',
                               'width': 5}

        self.scatterStyleComboBox = ttk.Combobox(self.tab2,
                                                 **scatterStyle_kwargs)

        self.lineOn.grid(row=thisrow, column=1, padx=(7, 0))
        self.lineStyleComboBox.grid(row=thisrow, column=2)
        self.scatterOn.grid(row=thisrow, column=3, padx=(22, 0))
        self.scatterStyleComboBox.grid(row=thisrow, column=4)

        ########################################
        # Row 3 - X Minimum and Maximum Values
        ########################################
        thisrow += 1

        self.xMin = None
        self.xMax = None
        self.xMinLabel = tk.Label(self.tab2, text='Min: ')
        self.xMaxLabel = tk.Label(self.tab2, text='Max: ')
        self.xMinEntry = tk.Entry(self.tab2, width=8)
        self.xMaxEntry = tk.Entry(self.tab2, width=8)
        self.xLimits = tk.BooleanVar(value=False)
        self.xLimitsRow = thisrow
        self.xLimitsBox = tk.Checkbutton(self.tab2,
                                         text='Modify X Limits',
                                         variable=self.xLimits,
                                         command=self.showXLimits)
        self.xLimitsBox.grid(row=thisrow, column=0, sticky=tk.W)
        ########################################
        # Row 4 - Y Minimum and Maximum Values
        ########################################
        thisrow += 1

        self.yMin = None
        self.yMax = None
        self.yMinLabel = tk.Label(self.tab2, text='Min: ')
        self.yMaxLabel = tk.Label(self.tab2, text='Max: ')
        self.yMinEntry = tk.Entry(self.tab2, width=8)
        self.yMaxEntry = tk.Entry(self.tab2, width=8)
        self.yLimits = tk.BooleanVar(value=False)
        self.yLimitsRow = thisrow
        self.yLimitsBox = tk.Checkbutton(self.tab2,
                                         text='Modify Y Limits',
                                         variable=self.yLimits,
                                         command=self.showYLimits)
        self.yLimitsBox.grid(row=thisrow, column=0, sticky=tk.W)

        ########################################
        # Row 5 - Z Minimum and Maximum Values
        ########################################
        thisrow += 1

        self.zMin = None
        self.zMax = None
        self.zMinLabel = tk.Label(self.tab2, text='Min: ')
        self.zMaxLabel = tk.Label(self.tab2, text='Max: ')
        self.zMinEntry = tk.Entry(self.tab2, width=8)
        self.zMaxEntry = tk.Entry(self.tab2, width=8)
        self.zLimits = tk.BooleanVar(value=False)
        self.zLimitsRow = thisrow
        self.zLimitsBox = tk.Checkbutton(self.tab2,
                                         text='Modify Z Limits',
                                         variable=self.zLimits,
                                         command=self.showZLimits)
        if self.dimensions.get() == 3:
            self.zLimitsBox.grid(row=thisrow, column=0, sticky=tk.W)

        ################################################################
        # Tab 3: Save Options
        ################################################################
        self.saveoptions_icon = tk.PhotoImage(file='images/save-disk.png')
        self.tab3 = ttk.Frame(self.tabs,)
        self.tabs.add(
                self.tab3,
                text='Saving Options',
                image=self.saveoptions_icon,   # The icon feature is awesome
                compound=tk.LEFT,)               # Places icon left of text

        ########################################
        # Row 0 - Output Directory
        ########################################
        self.outDirLabel = tk.Label(self.tab3, text='Output Directory: ')
        self.outDirLabel.grid(row=0, sticky=tk.W)

        self.outDirPath = tk.Text(self.tab3, relief=tk.SUNKEN)
        self.outDirPath.config(width=40, height=1.45)
        self.outDirPath.grid(row=0, column=1, columnspan=5, sticky=tk.W)

        self.outDirBrowseButton = tk.Button(self.tab3,
                                            text='Browse',
                                            height=1,
                                            command=self.getOutDir)
        self.outDirBrowseButton.grid(row=0, column=6, padx=4)

        ########################################
        # Row 1 - Image Save Type
        ########################################
        self.imageTypeOptions = ('JPG', 'PDF', 'PNG', 'TIFF')
        self.imageTypeLabel = tk.Label(self.tab3, text='Image Format: ')
        self.imageTypeLabel.grid(row=1, sticky=tk.W)
        self.imageType = tk.StringVar()

        # TODO: Change "state" to 'readonly' and implement extensions
        self.imageTypeComboBox = ttk.Combobox(self.tab3,
                                              textvariable=self.imageType,
                                              values=self.imageTypeOptions,
                                              state='disabled',
                                              width=20,)

        # Sets the default to PNG since it looks nice and is small
        self.imageTypeComboBox.set('PNG')
        self.imageTypeComboBox.grid(row=1, column=1, columnspan=2)

        ################################################################
        # Tab 4: Viewer
        ################################################################
        self.viewer_icon = tk.PhotoImage(file='images/three-dim-graph.png')
        self.tab4 = ttk.Frame(self.tabs,)
        self.tabs.add(
                self.tab4,
                text='Viewer',
                image=self.viewer_icon,   # The icon feature is awesome
                compound=tk.LEFT,)        # Places icon left of text

        ########################################
        # Row 0 - X Plot Column
        ########################################
        thisrow = 0
        self.x, self.y, self.z = tk.StringVar(), tk.StringVar(), tk.StringVar()
        self.xLabel = tk.Label(self.tab4, text='X=')
        self.xLabel.grid(row=thisrow, column=0, sticky=tk.W)
        self.xComboBox = ttk.Combobox(self.tab4, textvariable=self.x,
                                      values=self.plotCols, state='readonly',
                                      width=30)
        self.xComboBox.grid(row=thisrow, column=1)

        ########################################
        # Row 0 - X Plot Column
        ########################################
        thisrow += 1
        self.yLabel = tk.Label(self.tab4, text='Y=')
        self.yLabel.grid(row=thisrow, column=0, sticky=tk.W)
        self.yComboBox = ttk.Combobox(self.tab4, textvariable=self.y,
                                      values=self.plotCols, state='readonly',
                                      width=30)
        self.yComboBox.grid(row=thisrow, column=1)

        ########################################
        # Row 2 - X Plot Column
        ########################################
        thisrow += 1
        self.zLabel = tk.Label(self.tab4, text='Z=')
        self.zLabel.grid(row=thisrow, column=0, sticky=tk.W)
        self.zComboBox = ttk.Combobox(self.tab4, textvariable=self.z,
                                      values=self.plotCols, state='readonly',
                                      width=30)
        self.zComboBox.grid(row=thisrow, column=1)

    def getTopDir(self):
        """
        Opens a file browswer for the run files. Once selected,
        the chosen file path will show in the text field.
        The path can be typed in also.
        ** Only a directory can be selected
        """

        kwargs = {'title': 'Select Directory Containing Run(s)',
                  'initialdir': self.default_path(), }
        self.topDir = filedialog.askdirectory(**kwargs)
        if self.topDir != '':
            self.topDir = os.path.abspath(self.topDir)

        # Updates text widget with path (deletes old path)
        self.topDirPath.delete('1.0', tk.END)
        self.topDirPath.insert(1.0, self.topDir)

    def loadFromTopDir(self):
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
        self.missileFile = os.path.abspath(mfile)
        self.missileDF = pd.read_excel(self.missileFile)
        self.plotCols = [''] + [col for col, val
                                in self.missileDF.dtypes.items()
                                if val == np.dtype('float64')]
        self.xComboBox['values'] = self.plotCols
        self.yComboBox['values'] = self.plotCols
        self.zComboBox['values'] = self.plotCols

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

    def todo(self):
        pass

    def default_path(self):
        defaultPaths = {'windows': 'C:\\',
                        'unix': '/',
                        'linux': '//',
                        'macos': None,
                        'sunos': None,
                        }
        thisOS = platform.system().lower()
        return defaultPaths[thisOS]

    def setGraphDimensions(self):
        self.graphDimensions = self.dimensions.get()
        if self.graphDimensions == 3:
            self.zLimitsBox.grid(row=self.zLimitsRow, column=0, sticky=tk.W)
        else:
            self.zLimits.set(False)
            self.zLimitsBox.grid_remove()
            self.showZLimits()

    def setNumPlots(self):
        self.numPlots = int(self.numPlotsSpinBox.get())

    # Updates the options available based upon which radio button is selected
    def setPlotStyleOptions(self):
        if self.plotStyle.get() == 'line':
            self.lineStyleComboBox.config(state='readonly')
            self.scatterStyleComboBox.config(state='disabled')
        if self.plotStyle.get() == 'scatter':
            self.lineStyleComboBox.config(state='disabled')
            self.scatterStyleComboBox.config(state='readonly')

    def showXLimits(self):
        if self.xLimits.get():  # if checked
            self.xMinLabel.grid(row=self.xLimitsRow, column=1)
            self.xMinEntry.grid(row=self.xLimitsRow, column=2)
            self.xMaxLabel.grid(row=self.xLimitsRow, column=3)
            self.xMaxEntry.grid(row=self.xLimitsRow, column=4)
        else:
            self.xMinLabel.grid_remove()
            self.xMinEntry.grid_remove()
            self.xMaxLabel.grid_remove()
            self.xMaxEntry.grid_remove()

    def showYLimits(self):
        if self.yLimits.get():  # if checked
            self.yMinLabel.grid(row=self.yLimitsRow, column=1)
            self.yMinEntry.grid(row=self.yLimitsRow, column=2)
            self.yMaxLabel.grid(row=self.yLimitsRow, column=3)
            self.yMaxEntry.grid(row=self.yLimitsRow, column=4)
        else:
            self.yMinLabel.grid_remove()
            self.yMinEntry.grid_remove()
            self.yMaxLabel.grid_remove()
            self.yMaxEntry.grid_remove()

    def showZLimits(self):
        if self.zLimits.get():  # if checked
            self.zMinLabel.grid(row=self.zLimitsRow, column=1)
            self.zMinEntry.grid(row=self.zLimitsRow, column=2)
            self.zMaxLabel.grid(row=self.zLimitsRow, column=3)
            self.zMaxEntry.grid(row=self.zLimitsRow, column=4)
        else:
            self.zMinLabel.grid_remove()
            self.zMinEntry.grid_remove()
            self.zMaxLabel.grid_remove()
            self.zMaxEntry.grid_remove()


app = SimpleGUI()
try:
    app.mainloop()
except KeyboardInterrupt:
    app.destroy()
    print('Terminated')
