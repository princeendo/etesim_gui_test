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
import mplcursors
import time
import multiprocessing as mp
import numpy as np
import pandas as pd
import seaborn as sns

# Tkinter imports
import tkinter as tk
from tkinter import ttk

# matplotlib imports
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

# Imports and settings for Tkinter
import matplotlib
matplotlib.use("TkAgg")  # To use with Tkinter

mp.freeze_support()

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

        # This will allow us to have the hovering cursor over lines
        self.showCursor = False

        # Determines whether to use Matplotlib/Seaborn/etc.
        self.plotEngine = 'mpl'

        # Creating a Notebook seems to be the key to making tabs
        # Requesting the current setup guarantees the notebook is built
        # to fill the space allotted
        height, width = self.winfo_reqheight(), self.winfo_reqwidth()
        self.tabs = ttk.Notebook(self, height=height, width=width)
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

        # For some reason, icons need to be member variables to display
        self.inpIcon = tk.PhotoImage(file='images/input-data-1.png')
        self.viewIcon = tk.PhotoImage(file='images/three-dim-graph.png')

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Tab 1: Data Input
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        inputTab = ttk.Frame(parent,)
        iK = {'text': 'Data Input', 'image': self.inpIcon, 'compound': tk.LEFT}
        parent.add(inputTab, **iK)
        eb.buildInputElements(self, inputTab, )

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Tab 2: Visualizer
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        viewTab = ttk.Frame(parent,)
        vK = {'text': 'Viewer', 'image': self.viewIcon, 'compound': tk.LEFT}
        parent.add(viewTab, **vK)

        # - - - - - - - - - - - - - - - -
        # Holder for editor/viewer
        graphPanes = ttk.Panedwindow(viewTab, orient=tk.HORIZONTAL)
        graphPanes.pack(fill=tk.BOTH, expand=True)

        self.editPane, self.viewPane = eb.buildEditAndViewPanes(graphPanes)

        eb.buildEditorElements(self, self.editPane, self.plotCols,
                               self.availableRuns, self.waitToPlot,
                               self.startPlot)

        # Setting the starting run options
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

    def autosizer(self, tabs, event=None) -> None:
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
        h, w = (self.winfo_height() - 50, self.winfo_width() - 145)
        self.tabs.config(height=h, width=w)

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
                if self.gridMinor.get():
                    self.gridMinor.set(False)
                    self.status.set('Minor grid not allowed in XKCD Mode')
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
                if self.gridMinor.get():
                    self.gridMinor.set(False)
                    self.status.set('Minor grid not allowed in XKCD Mode')
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

        # Constructing dataframe that contains data for plotting
        pDF = self.plotDF()

        # Setting all possible permutations for plotting data
        # TODO: Figure out a less janky way to do this
        numDFs = sum([x.RunNumber.nunique() for x in
                      [pDF.query(f'Model=="{m}" and Instance=="{i}"')
                       for (m, i)
                       in itertools.product(pDF.Model.unique(),
                                            pDF.Instance.unique())]])

        self.autoColors = cm.rainbow(np.linspace(0, 1, numDFs))

        # Switching out status label for a plot progress bar
        self.status.hide()
        self.plotProgressFrame.pack(fill=tk.BOTH, side=tk.LEFT)

        # All the random options needed to plot
        plotOptions = self.plotOptions()

        # Looping through all possible unique IDs and model numbers
        # and plotting each individual DataFrame
        groups = ['RunNumber', 'Model', 'Instance']
        for dataPack in enumerate(pDF.groupby(groups)):
            k = dataPack[0]
            if k % 20 == 0:
                self.canvas.draw()
                self.plotProgress.set(100*(k+1)/(numDFs))
                self.plotProgressLbl.set(f'{k+1}/{numDFs} complete')
            makePlot(myplot, dataPack, plotOptions)

        # Removing the counter and setting status back to normal
        self.plotProgressFrame.pack_forget()
        self.status.show()

        if self.showCursor:
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
        
    def plotOptions(self):
        plotStyle = self.plotStyle.get()
        showAllRuns = self.showAllRuns.get()
        transparentRuns = self.transparentRuns.get()
        specialRun = self.run.get()
        autoColor = self.autoColor.get()
        plotColor = self.plotColorEntry.get()
        dimensions = self.dimensions
        lineStyle = self.lineStyle.get()
        scatterStyle = self.scatterStyle.get()
        colors = self.autoColors
        
        return (plotStyle, showAllRuns, transparentRuns,
                specialRun, autoColor, plotColor,
                dimensions, lineStyle, scatterStyle, colors)
    
def makePlot(ax, itPack, options):
    k, ((run, model, instance), df) = itPack
    
    plotStyle, showAllRuns, transparentRuns = options[0:3]
    specialRun, autoColor, plotColor = options[3:6]
    dimensions, lineStyle, scatterStyle, colors = options[6:10]

    shouldFade = not showAllRuns and transparentRuns and run != specialRun
    
    plot_kwargs = {'label': f'{run}: {model} - {instance}',
                   'alpha': 1.0 - (0.8 * shouldFade),
                   'color': colors[k] if autoColor else plotColor,
                   }

    plotlist = [df.x, df.y] + ([df.z] if dimensions == 3 else [])

    if plotStyle == 'line':
        ax.plot(*plotlist, **plot_kwargs, linestyle=lineStyle)
    else:
        ax.scatter(*plotlist, **plot_kwargs, marker=scatterStyle)
    return options


# To prevent this running automatically if imported
if __name__ == "__main__":
    app = SimpleGUI()
    try:
        assert Axes3D  # to silence the linter
        app.mainloop()
    except KeyboardInterrupt:
        app.destroy()
        print('Terminated')
