# -*- coding: utf-8 -*-

"""

A postprocessing GUI to generate 2D/3D plots for simulation data.

The interface is designed to support ETESim output data, but will hopefully
support more datatypes in the future.


Example
-------
    Upon loading the the GUI with the command below, you can press the
    "Load" button on the default path and it will pull in relevant data.

        $ python etesim_pp_gui.py

Todo
----
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

# File Imports
import callback_functions as cf
import element_builder as eb
import extra_functions as ef
import plot_options_functions as pof

# Module-Level Imports
import itertools
import os
import mplcursors
import time
import numpy as np
import pandas as pd
import seaborn as sns

# Tkinter imports
import tkinter as tk
from tkinter import messagebox as mb
from tkinter import ttk
from tkinter import filedialog
import tkinter.font as font
import tkinter.colorchooser as tkColorChooser

# matplotlib imports
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# The original function was deprecated so we're importing the new one
# to match tutorials more closely
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

# mplcursors imports
# from mpldatacursor import datacursor

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
        self.cursor = None
        self.titleColorRGB = (0, 0, 0)
        self.titleColorHex = tk.StringVar(value='#000000')
        self.plotColorRGB = (31, 119, 180)                  # matplotlib blue
        self.plotColorHex = tk.StringVar(value='#1f77b4')
        self.availableRuns = np.array([])

        # Determines whether to use Matplotlib/Seaborn/etc.
        self.plotEngine = 'mpl'

        # Creating a Notebook seems to be the key to making tabs
        # buildTabs() compartmentalizes the code for making the tabs
        self.tabs = ttk.Notebook(self,
                                 height=self.winfo_reqheight(),
                                 width=self.winfo_reqwidth())
        self.buildTabs(self.tabs)

        # Fills the entire GUI with the notebook and lets the GUI
        # resize the notebook as needed
        self.tabs.pack(fill=tk.BOTH)
        self.tabs.bind("<Configure>", self.autosizer)
        self.tabs.bind("<<NotebookTabChanged>>",
                       lambda _: cf.setStatusBarOptions(self))

        # Sets up the GUI to have a status bar along the bottom
        self.statusBar = ttk.Frame(self, height=100)
        self.statusBar.pack(side=tk.BOTTOM, fill=tk.BOTH)
        statusKwargs = {'fill': tk.BOTH, 'side': tk.LEFT,
                        'text': 'No file(s) loaded', 'relief': tk.FLAT,
                        'height': 1, 'bd': 1, }
        self.status = eb.guiTextLabel(self.statusBar, 'pack', **statusKwargs)
        self.status.show()

        # Adding the progress bar for updating the user on completion
        self.plotProgress = tk.DoubleVar()
        self.plotProgressFrame = ttk.Frame(self.statusBar,)
        self.plotProgressLbl = tk.StringVar(self.plotProgressFrame, '')
        self.plotProgressText = tk.Label(self.plotProgressFrame, text='',
                                         relief=tk.FLAT, height=1, bd=1,
                                         textvariable=self.plotProgressLbl)
        self.plotProgressBar = ttk.Progressbar(self.plotProgressFrame,
                                               length=200,
                                               orient=tk.HORIZONTAL,
                                               mode='determinate',
                                               maximum=100.0,
                                               value=0.0,
                                               variable=self.plotProgress,)
        self.plotProgressBar.grid(row=0, column=0)
        self.plotProgressText.grid(row=0, column=1)
        self.plotProgressFrame.pack(fill=tk.BOTH, side=tk.LEFT)
        self.plotProgressFrame.pack_forget()

        # Adds an xkcd-style Easter-Egg
        self.xkcdMode = tk.BooleanVar(value=False)
        self.xkcdModeCB = ttk.Checkbutton(self.statusBar,
                                          text='xkcd mode',
                                          variable=self.xkcdMode,
                                          command=lambda: self.startPlot(1), )
        # By default, this should not be seen on the data input tab
        self.xkcdModeCB.pack_forget()

    def buildTabs(self, parent: ttk.Notebook) -> None:
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
                                            command=lambda: cf.getTopDir(self))
        self.topDirBrowseButton.grid(row=0, column=6, padx=4)

        self.topDirLoadButton = tk.Button(
                                    self.inputTab,
                                    text='Load',
                                    height=1,
                                    command=lambda: cf.loadFromTopDir(self))
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
        # Row 0 - XYZ Plot Columns
        thisrow = 0
        self.fieldsFrame = ttk.LabelFrame(self.editPane, relief=tk.RIDGE,
                                          text="Fields to Plot",)
        self.fieldsFrame.grid(row=thisrow, column=1, sticky=tk.W, pady=(1, 0))

        eb.buildXYZFieldSelector(self, self.fieldsFrame, self.plotCols,
                                 self.startPlot)

        # - - - - - - - - - - - - - - - -
        # Row 1 - XYZ Min/Max Fields
        thisrow += 1
        self.xyzMinMaxFrame = ttk.LabelFrame(self.editPane,
                                             text="Set Limits",
                                             relief=tk.RIDGE)
        self.xyzMinMaxFrame.grid(row=thisrow, column=1, sticky=tk.W, pady=3,)
        
        
        eb.buildXYZMinMaxModifiers(self, self.xyzMinMaxFrame)
        

        # - - - - - - - - - - - - - - - -
        # Row 2 - Custom Title
        thisrow += 1
        self.titleLF = ttk.LabelFrame(self.editPane, text="Custom Title",
                                      relief=tk.RIDGE)
        self.titleLF.grid(row=thisrow, column=1, sticky=tk.W, pady=3)

        # - - - - - - - - - -
        # Row 2.0 - Text
        self.titleText = tk.StringVar()
        titlekwargs = {'width': 35, 'textvariable': self.titleText, }
        self.titleEntry = ttk.Entry(self.titleLF, **titlekwargs)
        self.titleEntry.insert(0, '')

        # Adds a waiting period for the user to stop typing
        self.titleEntry.bind('<Key>', self.waitToPlot)
        self.titleEntry.grid(row=0, column=0, sticky=tk.W, columnspan=5)

        # - - - - - - - - - -
        # Row 2.1 - Styling
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
                                command=lambda: cf.editTitleOptions(self, 'b'))
        self.boldTitleButton.grid(row=1, column=1,)

        # Italic button
        itFont = font.Font(size=10, slant="italic")
        self.itTitleButton = tk.Button(
                                self.titleLF, text="I", width=3,
                                relief=tk.FLAT,
                                font=itFont,
                                command=lambda: cf.editTitleOptions(self, 'i'))
        self.itTitleButton.grid(row=1, column=2,)

        # Title Color Picker
        tc_kwargs = {'width': 8, 'textvariable': self.titleColorHex, }
        self.titleColorEntry = ttk.Entry(self.titleLF, **tc_kwargs)

        # Adds a waiting period for the user to stop typing
        self.titleColorEntry.bind('<Key>', self.waitToPlot)
        self.titleColorEntry.grid(row=1, column=3, sticky=tk.W)

        # Setting up color wheel buttong
        self.titleColorWheel = tk.PhotoImage(file='images/color_wheel.png')
        self.titleColorButton = tk.Button(
                                    self.titleLF,
                                    image=self.titleColorWheel,
                                    command=lambda: cf.pickTitleColor(self))
        self.titleColorButton.grid(row=1, column=4,)

        # - - - - - - - - - - - - - - - -
        # Row 3 - Style Options
        thisrow += 1
        self.styleLF = ttk.LabelFrame(self.editPane, text="Plot Style",
                                      relief=tk.RIDGE)
        self.styleLF.grid(row=thisrow, column=1, sticky=tk.W, pady=3)

        # - - - - - - - - - -
        # Row 3.0 - Plot/Scatter
        self.plotStyle = tk.StringVar(self.styleLF, 'line')

        linekwargs = {'text': 'Line', 'var': self.plotStyle, 'value': 'line',
                      'command': lambda: cf.setPlotStyleOptions(self, ), }

        scatterkwargs = {'text': 'Scatter', 'var': self.plotStyle,
                         'value': 'scatter',
                         'command': lambda: cf.setPlotStyleOptions(self, ), }

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
        # Row 3.1 - Legend
        self.showLegend = tk.BooleanVar(value=True)
        self.legendLoc = tk.StringVar(self.styleLF, value='Best')

        legendCB_kwargs = {'text': 'Show Legend', 'variable': self.showLegend,
                           'command': lambda: cf.setLegendOptions(self,), }
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
        # Row 3.2 - Plot Color

        # Setting up whether the colors should be made automatically
        self.autoColor = tk.BooleanVar(value=True)
        ac_kwargs = {'text': 'Auto Color', 'variable': self.autoColor,
                     'command': lambda: cf.showHidePlotColors(self, ), }
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
                      'command': lambda: cf.pickPlotColor(self), }
        self.plotColorButton = tk.Button(self.styleLF, **pcb_kwargs)
        self.plotColorButton.grid(row=2, column=3, sticky=tk.W, padx=(5, 0))

        # - - - - - - - - - - - - - - - -
        # Row 4 - Additional Options
        thisrow += 1
        self.addOptsLF = ttk.LabelFrame(self.editPane, relief=tk.RIDGE,
                                        text="Additional Options",)
        self.addOptsLF.grid(row=thisrow, column=1, sticky=tk.W, pady=3,)

        # - - - - - - - - - -
        # Row 4.0 - Grid
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
        # Row 4.1 - Axis Labels
        self.showAxLabel = ttk.Label(self.addOptsLF, text='Axis Labels:',)
        self.showAxLabel.grid(row=1, column=0, sticky=tk.W, padx=(0, 2))
        self.showAxFrame = tk.Frame(self.addOptsLF)
        self.showAxFrame.grid(row=1, column=1, sticky=tk.W, columnspan=2)

        # ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
        # Row 4.1.0 - XYZ Labels
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
        # Row 5 - Run Traversal
        thisrow += 1
        self.runChoiceLF = ttk.LabelFrame(self.editPane, relief=tk.RIDGE,
                                          text="Run Viewer",)
        self.runChoiceLF.grid(row=thisrow, column=1, sticky=tk.W, pady=3,)

        # The switch for whether runs are plotted all together
        self.showAllRuns = tk.BooleanVar(value=True)

        # - - - - - - - - - -
        # Row 5.0 - Show All Runs
        allruns_kwargs = {'text': 'All', 'var': self.showAllRuns,
                          'value': True, 'command': lambda: self.startPlot(1)}

        self.allRunsRB = ttk.Radiobutton(self.runChoiceLF, **allruns_kwargs,)
        self.allRunsRB.grid(row=0, column=0, columnspan=1, sticky=tk.W)

        # - - - - - - - - - -
        # Row 5.1 - Show Some Runs
        someruns_kwargs = {'text': 'Select', 'var': self.showAllRuns,
                           'value': False,
                           'command': lambda: self.startPlot(1)}
        self.someRunsRB = ttk.Radiobutton(self.runChoiceLF, **someruns_kwargs,)
        self.someRunsRB.grid(row=0, column=1, columnspan=1, sticky=tk.W)

        # Setting up the chooser for the individual run
        self.run = tk.IntVar()
        run_kwargs = {'values': self.availableRuns.tolist(), 'width': 4,
                      'command': lambda: self.startPlot(1), 'wrap': True,
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

        cf.setRunOptions(self, )

    

    

    ####################################################################
    # Utility functions
    ####################################################################
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

        # The columns we need in addition to the x/y/z data
        keepCols = ['RunNumber', 'Model', 'Instance']

        # Setting up a renaming convention to make plotting easier
        xyzRenamer = {self.xCol.get(): 'x', self.yCol.get(): 'y',
                      self.zCol.get(): 'z'}

        # Determining which columns to keep
        plotCols = [self.xCol.get(), self.yCol.get()]
        if self.dimensions == 3:
            plotCols.append(self.zCol.get())

        # Downselecting DataFrame based on these columns
        # Keeping Unique ID so we can plot each ID separately
        pDF = self.missileDF[keepCols + plotCols].copy()

        # If we don't want to show all the runs and don't
        # want them to be transparent, we can downselect the values now
        if not self.showAllRuns.get() and not self.transparentRuns.get():
            pDF = pDF.query(f'RunNumber=={self.run.get()}').copy()

        # This will allow us to reference plotDF.x
        # instead of having to call plotDF[self.xCol.get()], for example
        pDF.rename(columns=xyzRenamer, inplace=True)

        if self.plotEngine == 'mpl':   # No need for extra work here
            return pDF
        else:
            return ef.seabornDF(self, pDF)

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
        startTime = time.time()

        # If there's no reason to update, don't update
        if event is None:
            print(event, item, mode)    # This is mostly for debugging
            return

        if self.plotEngine == 'mpl':
            self.startMatPlot(startTime, event, item, mode)
        elif self.plotEngine == 'sns':
            self.startSNSPlot(startTime, event, item, mode)

    def startSNSPlot(self, startTime, event=None,
                     item=None, mode=None) -> None:

        # Close old figure and toolbar if they already exist
        if None not in (self.figure, self.canvas, self.toolbar):
            plt.close(self.figure)
            self.canvas.get_tk_widget().pack_forget()
            self.toolbar.pack_forget()

        # Loading data for plotting
        cf.setVals(self, )

        # Setting the run numbers to consider
        cf.setRunOptions(self, )

        # If there is nothing to plot, leave canvas blank
        if self.dimensions == 0:
            return

        # Settng up canvas to draw plot
        if self.xkcdMode.get():             # Easter Egg Mode
            with plt.xkcd():
                self.figure = plt.Figure(figsize=(6, 4))
                self.finishSNSPlot(startTime)
        else:
            self.figure = plt.Figure(figsize=(3, 2))
            self.finishSNSPlot(startTime)

    def startMatPlot(self, startTime, event=None,
                     item=None, mode=None) -> None:

        # Close old figure and toolbar if they already exist
        if None not in (self.figure, self.canvas, self.toolbar):
            plt.close(self.figure)
            self.canvas.get_tk_widget().pack_forget()
            self.toolbar.pack_forget()

        # Loading data for plotting
        cf.setVals(self, )

        # Setting the run numbers to consider
        cf.setRunOptions(self, )

        # If there is nothing to plot, leave canvas blank
        if self.dimensions == 0:
            return

        # Settng up canvas to draw plot
        if self.xkcdMode.get():             # Easter Egg Mode
            with plt.xkcd():
                self.figure = plt.Figure(figsize=(6, 4))
                self.finishMatPlot(startTime)
        else:
            self.figure = plt.Figure(figsize=(3, 2))
            self.finishMatPlot(startTime)

    def finishMatPlot(self, startTime: float) -> None:
        """
        Generates a new plot on the figure set up in startPlot.

        Parameters
        ----------
        startTime : float
            The time plotting began. Used to update the user on total
            rendering time.

        Returns
        -------
        None

        """

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.viewPane)
        self.canvas.draw()

        # Setting up subplot for showing all the plots
        subplot_kwargs = {'projection': '3d' if self.dimensions == 3 else None}
        myplot = self.figure.add_subplot(111, **subplot_kwargs)

        # This may need to be edited for multiple graph support
        plot_kwargs = {}

        # If autocoloring is turned off, set the color for the graph
        if not self.autoColor.get():
            plot_kwargs = {'color': self.plotColorEntry.get(), }

        # Looping through all possible unique IDs and model numbers
        # and plotting each individual DataFrame
        groups = ['RunNumber', 'Model', 'Instance']

        # Constructing dataframe that contains data for plotting
        pDF = self.plotDF()

        # Setting all possible permutations for plotting data
        numDFs = sum([x.RunNumber.nunique() for x in
                      [pDF.query(f'Model=="{m}" and Instance=="{i}"')
                       for (m, i)
                       in itertools.product(pDF.Model.unique(),
                                            pDF.Instance.unique())]])

        colors = cm.rainbow(np.linspace(0, 1, numDFs))

        # Switching out status label for a plot progress bar
        self.status.hide()
        self.plotProgressFrame.pack(fill=tk.BOTH, side=tk.LEFT)

        for k, ((run, model, instance), df) in enumerate(pDF.groupby(groups)):
            dfKwargs = {'kind': self.plotStyle.get(), 'ax': myplot}
            plot_kwargs['label'] = f'{run}: {model} - {instance}'

            # If the transparency setting is on, we want to highlight
            # only the run of interest
            if (
              not self.showAllRuns.get()
              and self.transparentRuns.get()
              and run != self.run.get()):
                plot_kwargs['alpha'] = 0.2
            else:
                plot_kwargs['alpha'] = 1.0

            dfKwargs.update(plot_kwargs)
            if self.autoColor.get():
                plot_kwargs['color'] = colors[k]
                dfKwargs['color'] = [colors[k]] * df.shape[0]
            else:
                plot_kwargs['color'] = self.plotColorEntry.get()

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

            # Updating the user on progress
            self.canvas.draw()
            self.plotProgress.set(100*(k+1)/(numDFs))
            self.plotProgressLbl.set(f'{k+1}/{numDFs} complete')

        # Removing the counter and setting status back to normal
        self.plotProgressFrame.pack_forget()
        self.status.show()

        self.cursor = mplcursors.cursor(myplot, hover=True)

        # Show legend if selected
        if self.showLegend.get():
            legend_kwargs = {'title': 'Run Number: Element - Instance',
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
        if self.gridMajor.get() and self.dimensions == 2:
            myplot.grid(b=True, which='major', alpha=0.8)
        if self.gridMinor.get() and self.dimensions == 2:
            myplot.minorticks_on()
            myplot.grid(b=True, which='minor', alpha=0.2, linestyle='--',)
        else:
            self.status.set('')

        # Setting the min/max values for each variable
        (xMin, xMax, yMin, yMax, zMin, zMax) = pof.getLimits(self, myplot)
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

        # Updating the user on the time it took to plot
        totalTime = time.time() - startTime
        self.status.set(f'Plot rendered in {totalTime:.1f}s')

    def finishSNSPlot(self, startTime: float) -> None:
        """
        Generates a new plot on the figure set up in startPlot.

        Parameters
        ----------
        startTime : float
            The time plotting began. Used to update the user on total
            rendering time.

        Returns
        -------
        None

        """
        self.cursor = None

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.viewPane)
        self.canvas.draw()

        myplot = self.figure.add_subplot(111,)

        # Constructing dataframe that contains data for plotting
        pDF = self.plotDF()

        # Switching out status label for a plot progress bar
        self.status.hide()
        self.plotProgressFrame.pack(fill=tk.BOTH, side=tk.LEFT)

        pStyle = self.plotStyle.get()

        if pStyle == 'line':
            sns.lineplot(x='x', y='y', hue='Model', data=pDF, ax=myplot)
        elif pStyle == 'scatter':
            sns.lmplot(x="x", y="y", hue="Model",  data=pDF, ax=myplot)

        # Removing the counter and setting status back to normal
        self.plotProgressFrame.pack_forget()
        self.status.show()

        # Show legend if selected
        if self.showLegend.get():
            legend_kwargs = {'fancybox': True, 'shadow': True, }

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
        if self.gridMajor.get() and self.dimensions == 2:
            myplot.grid(b=True, which='major', alpha=0.8)
        if self.gridMinor.get() and self.dimensions == 2:
            myplot.minorticks_on()
            myplot.grid(b=True, which='minor', alpha=0.2, linestyle='--',)
        else:
            self.status.set('')

        # Setting the min/max values for each variable
        (xMin, xMax, yMin, yMax, zMin, zMax) = pof.getLimits(myplot)
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

        # Updating the user on the time it took to plot
        totalTime = time.time() - startTime
        self.status.set(f'Plot rendered in {totalTime:.1f}s')


# To prevent this running automatically if imported
if __name__ == "__main__":
    app = SimpleGUI()
    try:
        assert Axes3D  # to silence the linter
        app.mainloop()
    except KeyboardInterrupt:
        app.destroy()
        print('Terminated')
